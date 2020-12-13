from enum import Enum
from typing import NewType
from uuid import UUID

import orjson
from pydantic import BaseModel


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class BaseEntity(BaseModel):
    id: UUID

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps


class SortOrder(Enum):
    ASC = 'asc'
    DESC = 'desc'


ModelType = NewType("ModelType", BaseEntity)
