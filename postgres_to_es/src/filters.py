import json
import logging
from typing import List

import backoff
import requests

from src.config import CONFIG
from src.models import FullMovie, Person, Roles, Genre
from src.wrappers import coroutine

logger = logging.getLogger(__name__)


class LoaderException(Exception):
    pass


@coroutine
def transform_person_data(target):
    while person := (yield):
        person = Person(**person)

        transformed_data = {
            "id": str(person.id),
            "full_name": person.full_name
        }
        target.send(transformed_data)


@coroutine
def transform_movie_data(target):
    """
    Transforms movie from PG-extracted data to ready-to-be-loaded to ES.
    """
    while movie := (yield):  # type: dict
        movie = FullMovie(**movie)
        writers = set()
        actors = set()
        directors = set()
        for name, id_, role in zip(movie.names, movie.persons_ids, movie.roles):
            if role is not None and name is not None and id_ is not None:
                role = Roles(role)
                person = Person(full_name=name, id=id_, role=role)
                if role == Roles.WRITER:
                    writers.add(person)
                elif role == Roles.ACTOR:
                    actors.add(person)
                elif role == Roles.DIRECTOR:
                    directors.add(person)
                else:
                    raise ValueError(f"Unhandled role {role}")
            elif role is None and name is None and id_ is None:
                logger.debug(f"Empty persons info for movie {movie.title} {movie.fw_id}")
            else:
                logger.error(f"Invalid persons at movie {movie}")
                raise ValueError("Invalid persons data")

        genres = set()
        for genre, id_ in zip(movie.genres, movie.genres_ids):
            if genre is not None and id_ is not None:
                genres.add(Genre(name=genre, id=id_))
            elif genre is None and id_ is None:
                logger.debug("Empty genre info, skipping")
            else:
                logger.error(f"Invalid genre at movie {movie}")
                raise ValueError("Invalid genres data")

        transformed_data = {
            "id": str(movie.fw_id),
            "imdb_rating": movie.rating,
            "genre": [{"id": str(g.id), "name": g.name} for g in genres],
            "title": movie.title,
            "description": movie.description,
            "directors_names": [d.full_name for d in directors],
            "actors_names": [a.full_name for a in actors],
            "writers_names": [w.full_name for w in writers],
            "actors": [{"id": str(a.id), "name": a.full_name} for a in actors],
            "writers": [{"id": str(w.id), "name": w.full_name} for w in writers],
            "directors": [{"id": str(w.id), "name": w.full_name} for w in directors]
        }
        target.send(transformed_data)


@coroutine
def transform_genre_data(target):
    """
    Transforms genre from PG-extracted data to ready-to-be-loaded to ES.
    """
    while genre := (yield):  # type: dict
        genre = Genre(
            id=genre['id'],
            name=genre['name'],
            description=genre.get('description'),
            created=genre.get('created'),
            modified=genre.get('modified')
        )
        transformed_data = {
            "id": str(genre.id),
            "name": genre.name,
            "description": genre.description,
        }
        target.send(transformed_data)


@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_time=CONFIG.ES_CONNECT_TIMEOUT)
def perform_loading(essences: List[dict], index_name: str):
    """
    Performs loading of provided movies to Elasticsearch with retries.
    :essences: List of movies or genres information.
    """
    request_body = []
    logger.debug("Loading another batch to ES")
    for essence in essences:
        header = {
            "index": {
                "_index": index_name,
                "_id": essence["id"]
            }
        }
        request_body.append(json.dumps(header))
        request_body.append(json.dumps(essence))

    request_body = "\n".join(request_body) + "\n"  # trailing \n is mandatory
    response = requests.post(
        url=f"{CONFIG.ELASTIC_URL}/_bulk",
        headers={"Content-Type": "application/x-ndjson"},
        data=request_body
    )
    response.raise_for_status()
    if response.json()["errors"]:
        logger.error(f"Error during loading to ES. {response.text}")
        raise RuntimeError(f"Error during loading data to ES.")


@coroutine
def load_essences(index_name: str):
    """
    Loads essences batch to Elasticsearch.
    """
    essences_loaded = 0
    essences_batch = []
    try:
        while essence_to_load := (yield):  # type: dict
            essences_batch.append(essence_to_load)
            if len(essences_batch) >= CONFIG.LOAD_TO_ES_BY:
                perform_loading(essences_batch, index_name)
                essences_loaded += len(essences_batch)
                essences_batch = []
    except GeneratorExit:
        logger.debug("Generator exit, loading last batch")
        if len(essences_batch) > 0:
            perform_loading(essences_batch, index_name)

        essences_loaded += len(essences_batch)
        logger.info(f"Loaded {essences_loaded} to {index_name} during this iteration")
