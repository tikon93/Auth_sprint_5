import datetime
import logging
from typing import List

import backoff
import psycopg2
from psycopg2.extensions import cursor as _cursor
from psycopg2.extras import DictCursor

from src.config import CONFIG
from src.consts import DEFAULT_DATE
from src.state import State
from src.wrappers import coroutine

logger = logging.getLogger(__name__)
DSN = {"dbname": CONFIG.DB_NAME, "user": CONFIG.DB_USER, "password": CONFIG.DB_PASSWORD, "host": CONFIG.DB_HOST,
       "port": CONFIG.DB_PORT}


def get_movies_by_ids(ids: List[str], cursor: _cursor) -> List[dict]:
    """
    Retrieves full movies data.
    """
    logger.debug(f"Looking for {len(ids)} movies")
    args = ",".join(cursor.mogrify("%s", (_id,)).decode() for _id in ids)
    cursor.execute(f"""
    SELECT
        fw.id as fw_id, 
        fw.title, 
        fw.description, 
        fw.rating, 
        fw.created, 
        fw.modified, 
        array_agg(g.name) as genres,
        array_agg(g.id) as genres_ids,
        array_agg(p.full_name) as names,
        array_agg(pfw.role) as roles,
        array_agg(p.id) as persons_ids
    FROM content.film_work fw
    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
    LEFT JOIN content.person p ON p.id = pfw.person_id
    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
    LEFT JOIN content.genre g ON g.id = gfw.genre_id
    WHERE fw.id IN ({args})
    GROUP BY fw_id;
    """)
    movies = cursor.fetchall()
    logger.debug(f"Found {len(movies)} movies by ids")
    return movies


def fetch_updated_persons(cursor: _cursor, updated_after: datetime.datetime) -> List[dict]:
    """
    Extracts all persons updated after provided date.
    """
    cursor.execute(f"""
                SELECT id, modified, full_name
                FROM content.person
                WHERE modified > %s
                ORDER BY modified
                LIMIT {CONFIG.FETCH_FROM_PG_BY};
                """, (updated_after,))
    updated_persons = cursor.fetchall()
    logger.debug(f"Fetched {len(updated_persons)} persons")
    return updated_persons


def fetch_movies_by_persons(cursor: _cursor, persons: List[dict], updated_after: datetime.datetime):
    """
    Extracts movies where provided persons participate.
    Also filters movies by updated_at.
    """
    args = ",".join(cursor.mogrify("%s", (person["id"],)).decode() for person in persons)
    cursor.execute(f"""
                    SELECT fw.id, fw.modified 
                    FROM content.film_work fw 
                    LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id 
                    WHERE modified > %s AND pfw.person_id IN ({args}) 
                    ORDER BY fw.modified 
                    LIMIT {CONFIG.FETCH_FROM_PG_BY};
                    """, (updated_after,))

    linked_movies = cursor.fetchall()
    logger.debug(f"Fetched {len(linked_movies)} linked movies")
    return linked_movies


@backoff.on_exception(backoff.expo, psycopg2.errors.ConnectionException, max_time=CONFIG.PG_TIMEOUT_SEC)
@coroutine
def extract_movies_updated_due_to_person_change(target, state: State):
    """
    Data producer for movies which necessary to be synced due to linked persons data change.
    """
    with psycopg2.connect(**DSN, cursor_factory=DictCursor).cursor() as cursor:  # type: _cursor
        date_start = last_person_synced = state.last_person_for_movies_synced_at

        while updated_persons := fetch_updated_persons(cursor, last_person_synced):
            # we don"t care when movie"s data changed - updated_at will not be changed if person data changes
            # updated_at is used as cursor to iterate over movies
            last_movie_synced_by_persons_at = DEFAULT_DATE
            while linked_movies := fetch_movies_by_persons(cursor, updated_persons, last_movie_synced_by_persons_at):
                movies_ids_not_synced = [m["id"] for m in linked_movies if str(m["id"]) not in state.movies_synced]

                if movies_ids_not_synced:
                    movies_to_send = get_movies_by_ids(movies_ids_not_synced, cursor)
                    for movie in movies_to_send:
                        target.send(movie)
                        state.add_movies_synced([str(movie["fw_id"])])

                logger.debug(f"Synced all movies updated after {last_movie_synced_by_persons_at} "
                             f"for persons updated after {last_person_synced}. Searching for more movies")

                last_movie_synced_by_persons_at = linked_movies[-1]["modified"]

            last_person_synced = updated_persons[-1]["modified"]
            state.set_last_person_for_movies_synced_at(last_person_synced)

        logger.debug(f"All movies linked with persons updated after {date_start}, shutting down receiving coroutine")


def fetch_movies_updated_after(cursor: _cursor, updated_after: datetime.datetime) -> List[dict]:
    """
    Returns all movies updated after provided date.
    """
    cursor.execute(f"""
                SELECT id, modified
                FROM content.film_work
                WHERE modified > %s
                ORDER BY modified
                LIMIT {CONFIG.FETCH_FROM_PG_BY};
                """, (updated_after,))

    updated_movies = cursor.fetchall()
    logger.debug(f"Fetched {len(updated_movies)} linked movies")
    return updated_movies


@backoff.on_exception(backoff.expo, psycopg2.errors.ConnectionException, max_time=CONFIG.PG_TIMEOUT_SEC)
@coroutine
def extract_movies_updated_due_to_movie_change(target, state: State):
    """
    Data producer for movies which necessary to be synced due to movies itself change.
    Assumes that if genre or person relation is added/deleted to/from movie - movie"s updated_at field will be changed.
    """
    with psycopg2.connect(**DSN, cursor_factory=DictCursor).cursor() as cursor:  # type: _cursor

        date_start = last_movie_synced_at = state.last_movie_synced_at
        while updated_movies := fetch_movies_updated_after(cursor, last_movie_synced_at):
            movies_ids_not_synced = [m["id"] for m in updated_movies if str(m["id"]) not in state.movies_synced]

            if movies_ids_not_synced:
                movies_to_send = get_movies_by_ids(movies_ids_not_synced, cursor)
                for movie in movies_to_send:
                    target.send(movie)
                    state.add_movies_synced([str(movie["fw_id"])])

            logger.debug(f"Synced all movies updated after {last_movie_synced_at} Searching for more movies")
            last_movie_synced_at = updated_movies[-1]["modified"]
            state.set_last_movie_synced_at(last_movie_synced_at)

        logger.debug(f"Finished with movies updated due to movie data change after {date_start}")


@backoff.on_exception(backoff.expo, psycopg2.errors.ConnectionException, max_time=CONFIG.PG_TIMEOUT_SEC)
@coroutine
def extract_genres_updated_due_to_genre_change(target, state: State):
    """
    Data producer for genres which necessary to be synced due to genres itself change.
    """
    with psycopg2.connect(**DSN, cursor_factory=DictCursor).cursor() as cursor:  # type: _cursor

        date_start = last_genre_synced_at = state.last_genre_for_genres_synced_at
        while updated_genres := fetch_updated_genres(cursor, last_genre_synced_at):
            genres_synced = state.genres_for_genres_synced
            genres_to_send = [g for g in updated_genres if str(g["id"]) not in genres_synced]

            for genre in genres_to_send:
                target.send(genre)
                state.add_genres_for_genres_synced([str(genre["id"])])

            logger.debug(f"Synced all genres updated after {last_genre_synced_at} Searching for more genres")
            last_genre_synced_at = updated_genres[-1]["modified"]
            state.set_last_genre_for_genres_synced_at(last_genre_synced_at)

        logger.debug(f"Finished with genres updated due to genre data change after {date_start}")


def fetch_updated_genres(cursor: _cursor, updated_after: datetime.datetime) -> List[dict]:
    """
    Returns all genres updated after provided date
    """
    cursor.execute(f"""
                SELECT
                    id,
                    name,
                    description,
                    modified
                FROM content.genre
                WHERE modified > %s
                ORDER BY modified
                LIMIT {CONFIG.FETCH_FROM_PG_BY};
                """, (updated_after,))
    updated_genres = cursor.fetchall()
    logger.debug(f"Fetched {len(updated_genres)} genres")
    return updated_genres


def fetch_movies_by_genres(cursor: _cursor, genres: List[dict], movie_updated_after: datetime.datetime) -> List[dict]:
    """
    Returns all movies related to provided genres list.
    Also filters movies by provided updated_at field.
    """
    args = ",".join(cursor.mogrify("%s", (genre["id"],)).decode() for genre in genres)
    cursor.execute(f"""
                    SELECT fw.id, fw.modified 
                    FROM content.film_work fw 
                    LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id 
                    WHERE modified > %s AND gfw.genre_id IN ({args}) 
                    ORDER BY fw.modified 
                    LIMIT {CONFIG.FETCH_FROM_PG_BY};
                    """, (movie_updated_after,))

    linked_movies = cursor.fetchall()
    logger.debug(f"Fetched {len(linked_movies)} linked movies")
    return linked_movies


@backoff.on_exception(backoff.expo, psycopg2.errors.ConnectionException, max_time=CONFIG.PG_TIMEOUT_SEC)
@coroutine
def extract_movies_updated_due_to_genre_change(target, state: State):
    """
    Data producer for movies which necessary to be synced due to linked genre data change.
    """
    with psycopg2.connect(**DSN, cursor_factory=DictCursor).cursor() as cursor:  # type: _cursor

        date_start = last_genre_synced = state.last_genre_synced_at
        while updated_genres := fetch_updated_genres(cursor, last_genre_synced):

            last_movie_synced_by_genre = DEFAULT_DATE
            while linked_movies := fetch_movies_by_genres(cursor, updated_genres, last_movie_synced_by_genre):
                movies_ids_not_synced = [m["id"] for m in linked_movies if str(m["id"]) not in state.movies_synced]

                if movies_ids_not_synced:
                    movies_to_send = get_movies_by_ids(movies_ids_not_synced, cursor)
                    for movie in movies_to_send:
                        target.send(movie)
                        state.add_movies_synced([str(movie["fw_id"])])

                logger.debug(f"Synced all movies updated after {last_movie_synced_by_genre} "
                             f"for genres updated after {last_genre_synced}. Searching for more movies")
                last_movie_synced_by_genre = linked_movies[-1]["modified"]

            last_genre_synced = updated_genres[-1]["modified"]
            state.set_last_genre_synced_at(last_genre_synced)

        logger.debug(f"All movies linked with genres updated after {date_start}")


@backoff.on_exception(backoff.expo, psycopg2.errors.ConnectionException, max_time=CONFIG.PG_TIMEOUT_SEC)
@coroutine
def extract_updated_persons(target, state: State):
    """
    Data producer for updated persons since last sync.
    """
    with psycopg2.connect(**DSN, cursor_factory=DictCursor).cursor() as cursor:  # type: _cursor
        date_start = last_person_synced = state.last_person_synced_at

        while updated_persons := fetch_updated_persons(cursor, last_person_synced):
            persons_not_synced = [p for p in updated_persons if str(p["id"] not in state.persons_synced)]
            for person in persons_not_synced:
                target.send(person)
                state.add_persons_synced([str(person["id"])])

            last_person_synced = updated_persons[-1]["modified"]
            state.set_last_person_synced_at(last_person_synced)

        logger.debug(f"All persons updated after {date_start} synced, shutting down receiving coroutine")
