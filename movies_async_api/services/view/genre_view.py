import logging
from enum import Enum
from functools import lru_cache
from typing import Optional, List, Dict
from uuid import UUID

from fastapi import Depends

from db.cache import get_genre_cache
from db.cache.abstract import AbstractEntityCacher
from db.storage import get_genre_storage
from db.storage.abstract import AbstractStorageGetter
from models.base import SortOrder
from models.genre import Genre
from .base import BaseView

logger = logging.getLogger(__name__)


class GenreView(BaseView):

    async def get_genre(self, entity_id: UUID) -> Optional[Genre]:
        return await self.get_entity(entity_id)

    async def get_genres(
            self,
            page: int,
            per_page: int,
            sort_order: SortOrder,
            sort_by: Optional[Enum] = None,
            filters: Optional[Dict[Enum, str]] = None,
            logical_and_between_filters: bool = True
    ) -> List[Genre]:

        return await self.get_entities(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters,
            logical_and_between_filters=logical_and_between_filters
        )


@lru_cache()
def get_genre_service(
        cache: AbstractEntityCacher = Depends(get_genre_cache),
        storage: AbstractStorageGetter = Depends(get_genre_storage),
) -> GenreView:
    return GenreView(storage=storage, cache=cache)
