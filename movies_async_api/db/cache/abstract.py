from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from models.base import ModelType


class CacherBackoffException(Exception):
    pass


class AbstractEntityCacher(ABC):

    @abstractmethod
    async def get_entity(self, entity_id: UUID) -> Optional[ModelType]:
        pass

    @abstractmethod
    async def put_entity(self, entity: ModelType):
        pass

    @abstractmethod
    async def get_entities(self, page: int, per_page: int, **kwargs) -> Optional[List[ModelType]]:
        pass

    @abstractmethod
    async def put_entities(self, entities: List[ModelType], page: int, per_page: int, **kwargs):
        pass
