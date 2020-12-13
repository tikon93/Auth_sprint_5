from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import APIRouter, Depends

from db.elastic import get_elastic
from db.redis import get_redis

router = APIRouter()


@router.get("/")
async def get_health_status(redis: Redis = Depends(get_redis), elastic: AsyncElasticsearch = Depends(get_elastic)):
    await redis.ping()
    await elastic.ping()
    return "OK"
