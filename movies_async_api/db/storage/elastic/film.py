import logging
from enum import Enum
from typing import List, Dict

from elasticsearch import AsyncElasticsearch

from core.config import ES_MOVIES_INDEX
from db.storage.abstract import AbstractStorageWithSearch
from models.film import Film, SortBy, FilterBy
from .base import BaseESStorageGetter

logger = logging.getLogger(__name__)


class FilmESStorageGetter(AbstractStorageWithSearch, BaseESStorageGetter):

    def __init__(self, elastic_driver: AsyncElasticsearch):
        super().__init__(elastic_driver=elastic_driver, elastic_index=ES_MOVIES_INDEX, model_cls=Film)

    @property
    def filter_fields(self) -> Dict[Enum, str]:
        return {
            FilterBy.GENRE: 'genre',
            FilterBy.ACTOR: 'actors',
            FilterBy.WRITER: 'writers',
            FilterBy.DIRECTOR: 'directors'
        }

    @property
    def sort_values(self) -> Dict[SortBy, str]:
        return {SortBy.TITLE: 'title.raw', SortBy.IMDB_RATING: 'imdb_rating'}

    async def non_strict_search(
            self,
            search: str,
            page: int,
            per_page: int
    ) -> List[Film]:

        logger.debug(f"Performing non-strict search on films by search string {search}")
        query = {
            "multi_match": {
                "query": search,
                "fuzziness": "auto",
                "fields": ["title^5", "description^4", "genre^3", "actors_names^3", "writers_names^2", "director"]
            }
        }

        return await self._perform_query(page=page, per_page=per_page, sort=[], query=query)
