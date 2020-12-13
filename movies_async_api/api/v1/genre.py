from http import HTTPStatus
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from core.config import DEFAULT_PER_PAGE
from models.base import SortOrder
from models.film import SortBy as FilmsSortBy, FilterBy
from models.genre import SortBy
from services.view.film_view import FilmView, get_films_service
from services.view.genre_view import GenreView, get_genre_service
from .common_response_models import ShortFilm, GenreWithMovies, ResponseGenre

router = APIRouter()


@router.get('/{genre_id}', response_model=GenreWithMovies)
async def genre_info(
        genre_id: UUID,
        page: int = Query(1, ge=1, alias="page[number]"),
        per_page: int = Query(DEFAULT_PER_PAGE, alias="page[size]"),
        genre_service: GenreView = Depends(get_genre_service),
        films_service: FilmView = Depends(get_films_service)
) -> GenreWithMovies:
    genre = await genre_service.get_genre(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')

    related_films_filter = {FilterBy.GENRE: str(genre_id)}
    related_films = await films_service.get_films(
        page=page,
        per_page=per_page,
        sort_by=FilmsSortBy.IMDB_RATING,
        sort_order=SortOrder.DESC,
        filters=related_films_filter
    )
    short_movies = [ShortFilm(uuid=film.id, imdb_rating=film.imdb_rating, title=film.title)
                    for film in related_films]
    return GenreWithMovies(uuid=genre.id, name=genre.name, films=short_movies)


@router.get("/", response_model=List[ResponseGenre])
async def all_genres(
        page: int = Query(1, ge=1, alias="page[number]"),
        per_page: int = Query(DEFAULT_PER_PAGE, alias="page[size]"),
        genre_service: GenreView = Depends(get_genre_service)
) -> List[ResponseGenre]:
    genres = await genre_service.get_genres(
        page=page,
        per_page=per_page,
        sort_order=SortOrder.ASC,
        sort_by=SortBy.NAME
    )
    return [ResponseGenre(uuid=g.id, name=g.name) for g in genres]
