import logging
from enum import Enum
from functools import lru_cache
from typing import Optional, List, Dict
from uuid import UUID

from fastapi import Depends

from db.cache import get_person_cache
from db.cache.abstract import AbstractEntityCacher
from db.storage import get_person_storage
from db.storage.abstract import AbstractStorageWithSearch
from models.base import SortOrder
from models.person import Person
from .base import BaseView, service_backoff

logger = logging.getLogger(__name__)


class PersonView(BaseView):

    def __init__(self, cache: AbstractEntityCacher, storage: AbstractStorageWithSearch):
        super().__init__(storage=storage, cache=cache)
        self.storage: AbstractStorageWithSearch = storage

    async def get_person(self, entity_id: UUID) -> Optional[Person]:
        return await self.get_entity(entity_id)

    async def get_persons(
            self,
            page: int,
            per_page: int,
            sort_order: SortOrder,
            sort_by: Optional[Enum] = None,
            filters: Optional[Dict[Enum, str]] = None,
            logical_and_between_filters: bool = True
    ) -> List[Person]:

        return await self.get_entities(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters,
            logical_and_between_filters=logical_and_between_filters
        )

    @service_backoff
    async def search_persons(
            self,
            search: str,
            page: int,
            per_page: int
    ) -> List[Person]:

        persons = await self.cache.get_entities(page=page, per_page=per_page, search=search)
        if not persons:
            if not (persons := await self.storage.non_strict_search(search=search, page=page, per_page=per_page)):
                logger.debug("No persons found matching search")
                return []

            await self.cache.put_entities(persons, page=page, per_page=per_page, search=search)

        return persons


@lru_cache()
def get_person_service(
        cache: AbstractEntityCacher = Depends(get_person_cache),
        storage: AbstractStorageWithSearch = Depends(get_person_storage),
) -> PersonView:
    return PersonView(storage=storage, cache=cache)
