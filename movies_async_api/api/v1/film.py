from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from api.v1.common_response_models import ShortFilm, Film, ResponseGenre, ResponsePerson
from core.config import DEFAULT_PER_PAGE
from models.base import SortOrder
from models.film import SortBy, FilterBy
from services.view.film_view import FilmView, get_films_service

router = APIRouter()


@router.get('/{film_id}/', response_model=Film)
async def film_details(film_id: UUID, film_service: FilmView = Depends(get_films_service)) -> Film:
    film = await film_service.get_film(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')

    return Film(
        uuid=film.id,
        title=film.title,
        imdb_rating=film.imdb_rating,
        description=film.description,
        genre=[ResponseGenre(name=g["name"], uuid=UUID(g["id"])) for g in film.genre],
        actors=[ResponsePerson(full_name=p["name"], uuid=UUID(p["id"])) for p in film.actors],
        writers=[ResponsePerson(full_name=p["name"], uuid=UUID(p["id"])) for p in film.writers],
        directors=[ResponsePerson(full_name=p["name"], uuid=UUID(p["id"])) for p in film.directors]
    )


@router.get('/', response_model=List[ShortFilm])
async def all_films(
        page: int = Query(1, ge=1, alias="page[number]"),
        per_page: int = Query(DEFAULT_PER_PAGE, alias="page[size]"),
        sort: SortBy = SortBy.IMDB_RATING,
        sort_order: SortOrder = SortOrder.DESC,
        film_service: FilmView = Depends(get_films_service),
        genre: UUID = Query(None, alias="filter[genre]"),
        actor: UUID = Query(None, alias="filter[actor]"),
        writer: UUID = Query(None, alias="filter[writer]"),
) -> List[ShortFilm]:
    filters = {}
    if genre:
        filters[FilterBy.GENRE] = str(genre)
    if actor:
        filters[FilterBy.ACTOR] = str(actor)
    if writer:
        filters[FilterBy.WRITER] = str(writer)
    films = await film_service.get_films(
        page=page,
        per_page=per_page,
        sort_by=sort,
        sort_order=sort_order,
        filters=filters
    )
    return [ShortFilm(uuid=f.id, title=f.title, imdb_rating=f.imdb_rating) for f in films]


@router.get('/search', response_model=List[ShortFilm])
async def search(
        page: int = Query(1, ge=1, alias="page[number]"),
        per_page: int = Query(DEFAULT_PER_PAGE, alias="page[size]"),
        query: str = Query(..., min_length=1),
        film_service: FilmView = Depends(get_films_service)
) -> List[ShortFilm]:
    films = await film_service.search_films(
        page=page,
        per_page=per_page,
        search=query
    )
    return [ShortFilm(uuid=f.id, title=f.title, imdb_rating=f.imdb_rating) for f in films]
