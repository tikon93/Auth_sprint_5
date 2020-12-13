import logging
from enum import Enum
from functools import lru_cache
from typing import Optional, Dict, List
from uuid import UUID

from fastapi import Depends

from db.cache import get_film_cache
from db.cache.abstract import AbstractEntityCacher
from db.storage import get_film_storage
from db.storage.abstract import AbstractStorageWithSearch
from models.base import SortOrder
from models.film import Film
from .base import BaseView, service_backoff

logger = logging.getLogger(__name__)


class FilmView(BaseView):

    def __init__(self, cache: AbstractEntityCacher, storage: AbstractStorageWithSearch):
        super().__init__(storage=storage, cache=cache)
        self.storage: AbstractStorageWithSearch = storage

    async def get_film(self, film_id: UUID) -> Optional[Film]:
        return await self.get_entity(film_id)

    async def get_films(
            self,
            page: int,
            per_page: int,
            sort_order: SortOrder,
            sort_by: Optional[Enum] = None,
            filters: Optional[Dict[Enum, str]] = None,
            logical_and_between_filters: bool = True
    ) -> List[Film]:
        return await self.get_entities(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters,
            logical_and_between_filters=logical_and_between_filters
        )

    @service_backoff
    async def search_films(
            self,
            search: str,
            page: int,
            per_page: int
    ) -> List[Film]:

        films = await self.cache.get_entities(page=page, per_page=per_page, search=search)
        if not films:
            if not (films := await self.storage.non_strict_search(search=search, page=page, per_page=per_page)):
                logger.debug("No films found matching search")
                return []

            await self.cache.put_entities(films, page=page, per_page=per_page, search=search)

        return films


@lru_cache()
def get_films_service(
        cache: AbstractEntityCacher = Depends(get_film_cache),
        storage: AbstractStorageWithSearch = Depends(get_film_storage)
) -> FilmView:
    return FilmView(cache=cache, storage=storage)
