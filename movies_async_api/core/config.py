import os
from logging import config as logging_config
from urllib.parse import urlparse
from decouple import config
from core.logger import LOGGING

logging_config.dictConfig(LOGGING)

PROJECT_NAME = config('PROJECT_NAME', default='movies')

REDIS_HOST = config('REDIS_HOST', default='127.0.0.1')
REDIS_PORT = config('REDIS_PORT', default=6379)
REDIS_CACHE_EXPIRE_SEC = config('REDIS_CACHE_EXPIRE_SEC', default=60)

ELASTIC_URL = config('ELASTIC_URL', default='http://127.0.0.1:9200')
ELASTIC_HOST = urlparse(ELASTIC_URL).hostname
ELASTIC_PORT = urlparse(ELASTIC_URL).port
ES_MOVIES_INDEX = config('ES_MOVIES_INDEX', default='movies')
ES_PERSON_INDEX = config('ES_PERSON_INDEX', default='persons')
ES_GENRE_INDEX = config('ES_GENRE_INDEX', default='genres')

DEFAULT_PER_PAGE = config('DEFAULT_PER_PAGE', default=20)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLA_SERVICE_RESPONSE_MS = config('SLA_SERVICE_RESPONSE_MS', default=200)
AUTH_ENABLED = config('AUTH_ENABLED', default=True, cast=bool)
AUTH_CHECK_ENDPOINT = config("AUTH_CHECK_ENDPOINT", default='http://127.0.0.1:5000/session')
