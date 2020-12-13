from .base import BaseEntity
from enum import Enum


class Genre(BaseEntity):
    name: str


class SortBy(Enum):
    NAME = 'name'
