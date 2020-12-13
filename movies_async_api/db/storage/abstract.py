from abc import ABC, abstractmethod
from enum import Enum
from typing import List, Optional, Dict
from uuid import UUID

from models.base import ModelType, SortOrder


class StorageBackoffException(Exception):
    pass


class AbstractStorageGetter(ABC):

    @abstractmethod
    async def get_entity(self, entity_id: UUID, **kwargs) -> ModelType:
        pass

    @abstractmethod
    async def get_entities(
            self,
            page: int,
            per_page: int,
            sort_by: Optional[Enum] = None,
            sort_order: SortOrder = SortOrder.ASC,
            filters: Optional[Dict[Enum, List[str]]] = None,
            logical_and_between_filters: bool = True
    ) -> List[ModelType]:
        pass


class AbstractStorageWithSearch(AbstractStorageGetter):

    @abstractmethod
    async def non_strict_search(
            self,
            search: str,
            page: int,
            per_page: int
    ) -> List[ModelType]:
        pass
