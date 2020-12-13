from typing import Optional, List, Dict

from .base import BaseEntity
from enum import Enum


class Film(BaseEntity):
    id: str
    title: str
    description: Optional[str]
    imdb_rating: Optional[float]
    genre: Optional[List[Dict]]
    actors_names: Optional[List[str]]
    writers_names: Optional[List[str]]
    actors: Optional[List[Dict]]
    writers: Optional[List[Dict]]
    directors: Optional[List[Dict]]


class SortBy(Enum):
    TITLE = 'title'
    IMDB_RATING = 'imdb_rating'


class FilterBy(Enum):
    GENRE = "genre"
    ACTOR = "actor"
    WRITER = "writer"
    DIRECTOR = "director"
