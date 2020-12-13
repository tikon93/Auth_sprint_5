import enum

from .base import BaseEntity


class Person(BaseEntity):
    full_name: str


@enum.unique
class PossibleRoles(str, enum.Enum):
    writer = "writer"
    director = "director"
    actor = "actor"


class SortBy(enum.Enum):
    NAME = 'full_name'
