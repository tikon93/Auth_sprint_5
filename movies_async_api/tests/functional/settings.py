from decouple import config

ES_HOST: str = config("ELASTIC_HOST", default="127.0.0.1")
ES_PORT: int = config("ELASTIC_PORT", default=9200)

REDIS_HOST: str = config("REDIS_HOST", default="127.0.0.1")
REDIS_PORT: int = config("REDIS_PORT", default=6379)

ES_CONNECT_TIMEOUT: int = config("ES_CONNECT_TIMEOUT", default=20, cast=int)
REDIS_CONNECT_TIMEOUT: int = config("REDIS_CONNECT_TIMEOUT", default=20, cast=int)

API_URL: str = config("API_URL", default="http://0.0.0.0:8000/")

ES_MOVIES_INDEX_NAME: str = config("ES_MOVIES_INDEX_NAME", default="movies")
ES_GENRES_INDEX_NAME: str = config("ES_GENRES_INDEX_NAME", default="genres")
ES_PERSONS_INDEX_NAME: str = config("ES_PERSONS_INDEX_NAME", default="persons")

REDIS_CACHE_EXPIRE_SEC: int = config('REDIS_CACHE_EXPIRE_SEC', default=60, cast=int)
