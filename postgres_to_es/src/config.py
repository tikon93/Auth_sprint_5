from typing import Optional

from decouple import config
from pydantic import BaseModel, validator


class Config(BaseModel):
    DEBUG: bool = config("DEBUG", default=False, cast=bool)
    ETL_STATE_STORAGE_FOLDER = config("ETL_STATE_STORAGE_FOLDER", default="state/")
    UPDATES_CHECK_INTERVAL_SEC: int = config("UPDATES_CHECK_INTERVAL_SEC", default=60, cast=int)
    # database settings
    DB_HOST: str = config("POSTGRES_HOST", default=None)
    DB_PORT: int = config("POSTGRES_PORT", default=None)
    DB_NAME: str = config("POSTGRES_DB")
    DB_USER: str = config("POSTGRES_USER")
    DB_PASSWORD: Optional[str] = config("POSTGRES_PASSWORD", default=None)
    # extract from PG settings
    FETCH_FROM_PG_BY: int = config("FETCH_FROM_PG_BY", default=100, cast=int)
    PG_TIMEOUT_SEC: int = config("PG_TIMEOUT_SEC", default=60, cast=int)
    # es loading settings
    ELASTIC_URL: str = config("ELASTIC_URL", default="http://127.0.0.1:9200")
    LOAD_TO_ES_BY: int = config("LOAD_TO_ES_BY", default=100, cast=int)
    ES_MOVIES_INDEX: str = config("ES_MOVIES_INDEX", default="movies")
    ES_GENRE_INDEX: str = config("ES_GENRE_INDEX", default="genres")
    ES_PERSONS_INDEX: str = config("ES_PERSONS_INDEX", default="persons")
    ES_CONNECT_TIMEOUT = config("ES_CONNECT_TIMEOUT", default=60, cast=int)
    ES_STARTUP_TIMEOUT = config("ES_STARTUP_TIMEOUT", default=120, cast=int)

    @validator('UPDATES_CHECK_INTERVAL_SEC')
    def updates_check_interval_sec_correlates_with_hangup_timeout(cls, v, values):
        """
        Simplest validation, gives non-100% ensurance from misstreating process as hanged, but seems it's good enough.
        """
        if v * 2 > values.get("PROCESS_HANGUP_TIMEOUT_SEC", 600):
            raise ValueError("PROCESS_HANGUP_TIMEOUT_SEC must be at least twice more than process hang timeout")
        return v


CONFIG = Config()
