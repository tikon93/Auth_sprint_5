import logging
from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from core.config import DEFAULT_PER_PAGE
from models.base import SortOrder
from models.film import SortBy as FilmsSortBy, FilterBy
from models.person import PossibleRoles, SortBy
from services.view.film_view import FilmView, get_films_service
from services.view.person_view import PersonView, get_person_service
from .common_response_models import ShortFilm, PersonWithMovies, ResponsePerson

router = APIRouter()


logger = logging.getLogger(__name__)


@router.get('/{person_id}/', response_model=PersonWithMovies)
async def person_details(
        person_id: UUID,
        page: int = Query(1, ge=1, alias="page[number]"),
        per_page: int = Query(DEFAULT_PER_PAGE, alias="page[size]"),
        person_service: PersonView = Depends(get_person_service),
        films_service: FilmView = Depends(get_films_service),
) -> PersonWithMovies:
    person = await person_service.get_person(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    related_films_filter = {
        FilterBy.WRITER: str(person_id),
        FilterBy.DIRECTOR: str(person_id),
        FilterBy.ACTOR: str(person_id)
    }
    related_films = await films_service.get_films(
        page=page,
        per_page=per_page,
        sort_order=SortOrder.DESC,
        sort_by=FilmsSortBy.IMDB_RATING,
        filters=related_films_filter,
        logical_and_between_filters=False  # necessary to search all films, no matter which role it was
    )

    person_roles = {role: [] for role in PossibleRoles}
    short_movies = {movie.id: ShortFilm(uuid=movie.id,
                                        title=movie.title,
                                        imdb_rating=movie.imdb_rating)
                    for movie in related_films}
    logger.debug("Resolving roles")
    for movie in related_films:
        for role, entities in ((PossibleRoles.actor, movie.actors),
                               (PossibleRoles.writer, movie.writers),
                               (PossibleRoles.director, movie.directors)):
            if str(person_id) in [e["id"] for e in entities]:
                logger.debug(f"Person is {role} in {movie.title}")
                person_roles[role].append(short_movies[movie.id])

    return PersonWithMovies(uuid=person.id, full_name=person.full_name, roles=person_roles)


@router.get("/", response_model=List[ResponsePerson])
async def all_persons(
        page: int = Query(1, ge=1, alias="page[number]"),
        per_page: int = Query(DEFAULT_PER_PAGE, alias="page[size]"),
        sort_order: SortOrder = SortOrder.ASC,
        person_service: PersonView = Depends(get_person_service)
) -> List[ResponsePerson]:
    persons = await person_service.get_persons(
        page=page,
        per_page=per_page,
        sort_order=sort_order,
        sort_by=SortBy.NAME
    )
    return [ResponsePerson(uuid=p.id, full_name=p.full_name) for p in persons]


@router.get('/search', response_model=List[ResponsePerson])
async def search(
        page: int = Query(1, ge=1, alias="page[number]"),
        per_page: int = Query(DEFAULT_PER_PAGE, alias="page[size]"),
        query: str = Query(..., min_length=1),
        person_service: PersonView = Depends(get_person_service)
) -> List[ResponsePerson]:
    persons = await person_service.search_persons(
        page=page,
        per_page=per_page,
        search=query
    )
    return [ResponsePerson(uuid=p.id, full_name=p.full_name) for p in persons]
