import logging
from typing import Optional, List
from uuid import UUID

import orjson
from aioredis import Redis

from core.config import REDIS_CACHE_EXPIRE_SEC
from db.cache.abstract import AbstractEntityCacher, CacherBackoffException
from models.base import ModelType
from utils.wrappers import reraise_backoff_exceptions

logger = logging.getLogger(__name__)

REDIS_EXCEPTIONS_TO_BACKOFF = (ConnectionRefusedError,)


class RedisEntityCacher(AbstractEntityCacher):
    def __init__(self, redis: Redis, model_cls):
        self.redis = redis
        self.model_cls = model_cls

    @reraise_backoff_exceptions(exceptions_to_catch=REDIS_EXCEPTIONS_TO_BACKOFF,
                                exception_to_raise=CacherBackoffException)
    async def get_entity(self, entity_id: UUID) -> Optional[ModelType]:
        data = await self.redis.get(self._get_redis_key(entity_id=entity_id))
        if data is None:
            logger.debug(f"No entities with id {entity_id} found in cache")
            return None
        return self.model_cls.parse_raw(data)

    @reraise_backoff_exceptions(exceptions_to_catch=REDIS_EXCEPTIONS_TO_BACKOFF,
                                exception_to_raise=CacherBackoffException)
    async def put_entity(self, entity: ModelType):
        logger.debug(f"Putting entity {type(entity)} {entity.id} to cache")
        await self.redis.set(
            self._get_redis_key(entity_id=entity.id), entity.json(), expire=REDIS_CACHE_EXPIRE_SEC
        )

    @reraise_backoff_exceptions(exceptions_to_catch=REDIS_EXCEPTIONS_TO_BACKOFF,
                                exception_to_raise=CacherBackoffException)
    async def get_entities(self, page: int, per_page: int, **kwargs) -> Optional[List[ModelType]]:
        data = await self.redis.get(self._get_redis_key(page=page, per_page=per_page, **kwargs))

        if data is None:
            return data
        return [self.model_cls.parse_raw(entity) for entity in orjson.loads(data)]

    @reraise_backoff_exceptions(exceptions_to_catch=REDIS_EXCEPTIONS_TO_BACKOFF,
                                exception_to_raise=CacherBackoffException)
    async def put_entities(self, entities: List[ModelType], page: int, per_page: int, **kwargs):
        await self.redis.set(
            self._get_redis_key(page=page, per_page=per_page, **kwargs),
            orjson.dumps([entity.json() for entity in entities]),
            expire=REDIS_CACHE_EXPIRE_SEC
        )

    def _get_redis_key(self, **kwargs):
        return f"{self.model_cls.__name__}_{'_'.join([str(_[1]) for _ in sorted(kwargs.items())])}"
