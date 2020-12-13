import logging
from enum import Enum
from typing import Optional, List, Dict
from uuid import UUID

import backoff

from core.config import SLA_SERVICE_RESPONSE_MS
from db.cache.abstract import AbstractEntityCacher, CacherBackoffException
from db.storage.abstract import AbstractStorageGetter, StorageBackoffException
from models.base import ModelType, SortOrder

logger = logging.getLogger(__name__)

CACHE_INTERACTION_EXCEPTIONS = (ConnectionRefusedError,)
EXTERNAL_SERVICES_ITERACTION_MEAN_MS = 30
IO_BOUND_COST_MS = 10

SERVICE_BACKOFF_TIMEOUT = (SLA_SERVICE_RESPONSE_MS - EXTERNAL_SERVICES_ITERACTION_MEAN_MS - IO_BOUND_COST_MS) / 1000
EXCEPTIONS_TO_BACKOFF = (CacherBackoffException, StorageBackoffException)

service_backoff = backoff.on_exception(backoff.expo, max_time=SERVICE_BACKOFF_TIMEOUT, exception=EXCEPTIONS_TO_BACKOFF)


class BaseView:

    def __init__(self, storage: AbstractStorageGetter, cache: AbstractEntityCacher):
        self.storage: AbstractStorageGetter = storage
        self.cache: AbstractEntityCacher = cache

    @service_backoff
    async def get_entity(self, entity_id: UUID) -> Optional[ModelType]:
        entity = await self.cache.get_entity(entity_id)
        if entity is None:
            if (entity := await self.storage.get_entity(entity_id)) is None:
                logger.info(f"Entity with id {entity_id} not found")
                return None

            logger.debug(f"Putting entity with id {entity_id} to cache")
            await self.cache.put_entity(entity)

        return entity

    @service_backoff
    async def get_entities(
            self,
            page: int,
            per_page: int,
            sort_order: SortOrder,
            sort_by: Optional[Enum] = None,
            filters: Optional[Dict[Enum, List[str]]] = None,
            logical_and_between_filters: bool = True
    ) -> List[ModelType]:

        entities = await self.cache.get_entities(
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            filters=filters,
            sort_order=sort_order,
            logical_and_between_filters=logical_and_between_filters
        )
        if not entities:
            entities = await self.storage.get_entities(
                page=page,
                per_page=per_page,
                sort_by=sort_by,
                logical_and_between_filters=logical_and_between_filters,
                sort_order=sort_order,
                filters=filters,
            )
            if not entities:
                logger.debug("Empty list matching query")
                return []

            await self.cache.put_entities(entities, page=page, per_page=per_page, sort_by=sort_by, filters=filters,
                                          sort_order=sort_order,
                                          logical_and_between_filters=logical_and_between_filters)

        return entities
