import json
import logging

import backoff
import requests

from src.config import CONFIG
from src.consts import ES_GENRES_INDEX_CREATE_BODY, ES_PERSONS_INDEX_CREATE_BODY, ES_MOVIES_INDEX_CREATE_BODY

ES_INDEXES_BODIES = {
    CONFIG.ES_MOVIES_INDEX: ES_MOVIES_INDEX_CREATE_BODY,
    CONFIG.ES_GENRE_INDEX: ES_GENRES_INDEX_CREATE_BODY,
    CONFIG.ES_PERSONS_INDEX: ES_PERSONS_INDEX_CREATE_BODY
}


logger = logging.getLogger(__name__)


@backoff.on_exception(backoff.constant,
                      requests.exceptions.RequestException,
                      max_time=CONFIG.ES_STARTUP_TIMEOUT,
                      interval=10)
def ensure_es_index_exists(es_url: str, index_name: str):
    if index_name not in ES_INDEXES_BODIES:
        raise ValueError(f"Unable to create index {index_name}. Index body not found")
    request_body = ES_INDEXES_BODIES[index_name]
    headers = {"Content-Type": "application/json"}
    logger.info(f"Trying to create ES index {index_name}")
    response = requests.put(f"{es_url}/{index_name}", headers=headers, data=json.dumps(request_body))
    if response.status_code == 200:
        logger.info(f"Created new index {index_name}")
    elif response.status_code == 400 and "resource_already_exists_exception" in response.text:
        logger.info(f"Index {index_name} already exists, do nothing")
    else:
        logger.error(f"Error {response.status_code}")
        logger.error(response.text)
        raise RuntimeError(f"Unable to create index. Response {response.status_code}")
