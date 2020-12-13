from functools import lru_cache

from aioredis import Redis
from fastapi import Depends

from db.redis import get_redis
from models.film import Film
from models.genre import Genre
from models.person import Person
from .redis_cache import RedisEntityCacher


@lru_cache()
def get_person_cache(
        redis_driver: Redis = Depends(get_redis)
) -> RedisEntityCacher:
    return RedisEntityCacher(redis=redis_driver, model_cls=Person)


@lru_cache()
def get_genre_cache(
        redis_driver: Redis = Depends(get_redis)
) -> RedisEntityCacher:
    return RedisEntityCacher(redis=redis_driver, model_cls=Genre)


@lru_cache()
def get_film_cache(
        redis_driver: Redis = Depends(get_redis)
) -> RedisEntityCacher:
    return RedisEntityCacher(redis=redis_driver, model_cls=Film)
