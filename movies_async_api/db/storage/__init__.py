from functools import lru_cache

from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from .elastic.film import FilmESStorageGetter
from .elastic.genre import GenreESStorageGetter
from .elastic.person import PersonESStorageGetter


@lru_cache()
def get_person_storage(
        elastic_driver: AsyncElasticsearch = Depends(get_elastic)
) -> PersonESStorageGetter:
    return PersonESStorageGetter(elastic_driver=elastic_driver)


@lru_cache()
def get_film_storage(
    elastic_driver: AsyncElasticsearch = Depends(get_elastic)
) -> FilmESStorageGetter:
    return FilmESStorageGetter(elastic_driver=elastic_driver)


@lru_cache()
def get_genre_storage(
    elastic_driver: AsyncElasticsearch = Depends(get_elastic)
) -> GenreESStorageGetter:
    return GenreESStorageGetter(elastic_driver=elastic_driver)
