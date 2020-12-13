from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, List
from uuid import UUID


class Roles(Enum):
    DIRECTOR = "director"
    ACTOR = "actor"
    WRITER = "writer"


@dataclass(frozen=True)
class Person:
    full_name: str
    id: UUID
    role: Optional[Roles] = None  # standalone person doesn't have any role. Persons linked with movies have it
    modified: Optional[datetime] = None


@dataclass
class FullMovie:
    fw_id: UUID
    title: str
    description: Optional[str]
    rating: Optional[float]
    created: datetime
    modified: datetime
    genres: List[str]
    genres_ids: List[UUID]
    names: List[str]
    roles: List[str]
    persons_ids: List[UUID]


@dataclass(frozen=True)
class Genre:
    id: UUID
    name: str
    description: Optional[str] = None
    modified: Optional[datetime] = None
    created: Optional[datetime] = None
