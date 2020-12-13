from typing import Optional, List, Dict
from uuid import UUID

from pydantic import BaseModel


class ShortFilm(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: Optional[float]


class ResponsePerson(BaseModel):
    uuid: UUID
    full_name: str


class PersonWithMovies(ResponsePerson):
    roles: Dict[str, List[ShortFilm]]


class ResponseGenre(BaseModel):
    uuid: UUID
    name: str


class GenreWithMovies(ResponseGenre):
    films: List[ShortFilm]


class Film(BaseModel):
    uuid: UUID
    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    genre: Optional[List[ResponseGenre]]
    actors: Optional[List[ResponsePerson]]
    writers: Optional[List[ResponsePerson]]
    directors: Optional[List[ResponsePerson]]
