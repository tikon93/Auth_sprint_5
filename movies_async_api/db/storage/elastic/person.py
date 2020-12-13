import logging
from enum import Enum
from typing import Dict, List

from elasticsearch import AsyncElasticsearch

from core.config import ES_PERSON_INDEX
from models.person import Person, SortBy
from .base import BaseESStorageGetter
from db.storage.abstract import AbstractStorageWithSearch

logger = logging.getLogger(__name__)


class PersonESStorageGetter(AbstractStorageWithSearch, BaseESStorageGetter):

    def __init__(self, elastic_driver: AsyncElasticsearch):
        super().__init__(elastic_driver=elastic_driver, elastic_index=ES_PERSON_INDEX, model_cls=Person)

    @property
    def filter_fields(self) -> Dict[Enum, str]:
        return {}  # filtering is not supported for persons now

    @property
    def sort_values(self) -> Dict[SortBy, str]:
        return {SortBy.NAME: "full_name.raw"}

    async def non_strict_search(
            self,
            search: str,
            page: int,
            per_page: int
    ) -> List[Person]:

        logger.debug(f"Performing non-strict search on persons by search string {search}")
        query = {
            "multi_match": {
                "query": search,
                "fuzziness": "auto",
                "fields": ["full_name"]
            }
        }

        return await self._perform_query(page=page, per_page=per_page, sort=[], query=query)
