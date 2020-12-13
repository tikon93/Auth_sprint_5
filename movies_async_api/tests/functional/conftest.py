import json
import time
from typing import List, Dict, Any, Tuple

import pytest
import requests
from elasticsearch import Elasticsearch
from redis import Redis

from tests.functional.testdata.es_index_data import ES_BODY_BY_NAME
from tests.functional.settings import ES_HOST, ES_PORT, REDIS_HOST, REDIS_PORT, REDIS_CACHE_EXPIRE_SEC


@pytest.fixture(scope='session')
def es_client():
    client = Elasticsearch([{'host': ES_HOST, 'port': ES_PORT}])
    yield client
    client.close()


@pytest.fixture(scope='session')
def redis_client():
    client = Redis(host=REDIS_HOST, port=REDIS_PORT)
    yield client
    client.close()


@pytest.fixture(scope='session', autouse=True)
def es_indexes_setup():
    for index_name, index_body in ES_BODY_BY_NAME.items():
        response = requests.put(
            f"http://{ES_HOST}:{ES_PORT}/{index_name}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(index_body)
        )
        response.raise_for_status()
    yield
    for index_name, index_body in ES_BODY_BY_NAME.items():
        response = requests.delete(
            f"http://{ES_HOST}:{ES_PORT}/{index_name}",
        )
        response.raise_for_status()


@pytest.fixture(scope='function')
def es_data_setup(es_client, redis_client, request) -> List[Tuple[str, Dict[str, Any]]]:
    es_documents: List[Tuple[str, Dict[str, Any]]] = getattr(request, 'param', [])
    for es_index, es_body in es_documents:
        es_client.index(index=es_index, id=es_body['id'], body=es_body)
    time.sleep(1)
    yield es_documents
    for es_index, es_body in es_documents:
        es_client.delete(es_index, es_body['id'])


@pytest.fixture(scope='function')
def redis_data_setup(redis_client, request) -> List[Tuple[str, Any]]:
    redis_client.flushall()
    redis_documents: List[Tuple[str, Any]] = getattr(request, 'param', [])
    for redis_key, redis_value in redis_documents:
        redis_client.set(redis_key, json.dumps(redis_value), ex=REDIS_CACHE_EXPIRE_SEC)
    yield redis_documents
    redis_client.flushall()
