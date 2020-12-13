import datetime
import json
import logging
from typing import Any, List

from src.consts import DEFAULT_DATE, DATE_PARSE_PATTERN

logger = logging.getLogger(__name__)


class JsonFileStorage:
    def __init__(self, file_path: str = "state.json"):
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        with open(self.file_path, "w") as f:
            json.dump(state, f)

    def retrieve_state(self) -> dict:
        if self.file_path is None:
            logger.info("No state file provided. Continue with in-memory state")
            return {}

        try:
            with open(self.file_path) as f:
                data = json.load(f)

            return data

        except FileNotFoundError:
            logger.debug("No previously saved state. Initializing it with empty dict")
            self.save_state({})


class State:

    def __init__(self, storage_file: str):
        self.storage = JsonFileStorage(storage_file)
        self.state = self.retrieve_state()

    def retrieve_state(self) -> dict:
        data = self.storage.retrieve_state()
        if not data:
            return {}
        return data

    def set_state(self, key: str, value: Any) -> None:
        """Set state for specific key"""
        self.state[key] = value

        self.storage.save_state(self.state)

    def get_state(self, key: str) -> Any:
        """Retrieve state by specific key. Defaults to None."""
        return self.state.get(key)

    @property
    def last_person_synced_at(self) -> datetime.datetime:
        """
        updated_at of last person retrieved from Postgres during sync by persons.
        """
        date = self.get_state("last_person_synced_at")
        if date is None:
            return DEFAULT_DATE

        return datetime.datetime.strptime(date, DATE_PARSE_PATTERN)

    @property
    def last_person_for_movies_synced_at(self) -> datetime.datetime:
        """
        updated_at of last person retrieved from Postgres during sync by persons.
        """
        date = self.get_state("last_person_for_movies_synced_at")
        if date is None:
            return DEFAULT_DATE

        return datetime.datetime.strptime(date, DATE_PARSE_PATTERN)

    @property
    def last_genre_synced_at(self) -> datetime.datetime:
        """
        updated_at of last genre retrieved from Postgres during sync by genres.
        """
        date = self.get_state("last_genre_synced_at")
        if date is None:
            return DEFAULT_DATE

        return datetime.datetime.strptime(date, DATE_PARSE_PATTERN)

    @property
    def last_genre_for_genres_synced_at(self) -> datetime.datetime:
        """
        updated_at of last genre retrieved from Postgres during sync by genres for genres ElasticSearch index.
        """
        date = self.get_state(f"last_genre_for_genres_synced_at")
        if date is None:
            return DEFAULT_DATE

        return datetime.datetime.strptime(date, DATE_PARSE_PATTERN)

    @property
    def last_movie_synced_at(self) -> datetime.datetime:
        """
        updated_at of last movie retrieve from Postgres during sync by movies.
        """
        date = self.get_state("last_movie_synced_at")
        if date is None:
            return DEFAULT_DATE

        return datetime.datetime.strptime(date, DATE_PARSE_PATTERN)

    @property
    def movies_synced(self) -> tuple:
        """
        cache of movies which has been synced during this iteration. Necessary to avoid movies re-uploading -
        movie may be retrieved due to related person/genre change and also due to movie"s own data change.
        Cache stored as a tuple of movies ids.
        """
        movies = self.get_state("movies_synced")
        if movies is None:
            return tuple()

        return tuple(movies)

    @property
    def genres_synced(self) -> tuple:
        genres = self.get_state("genres_synced")
        if genres is None:
            return tuple()

        return tuple(genres)

    @property
    def genres_for_genres_synced(self):
        genres = self.get_state("genres_for_genres_synced")
        if genres is None:
            return tuple()

        return tuple(genres)

    @property
    def persons_synced(self) -> tuple:
        """
        Cache of persons updated during current iteration.
        Cache stored as a tuple of persons ids.
        """
        persons = self.get_state("persons_synced")
        if persons is None:
            return tuple()

        return tuple(persons)

    @property
    def last_full_state_sync_started_at(self) -> datetime.datetime:
        """
        date when last sync started. Necessary to check if other sync process stucked and re-launch it
        """
        date = self.get_state("last_full_state_sync_started_at")
        if date is None:
            return DEFAULT_DATE

        return datetime.datetime.strptime(date, DATE_PARSE_PATTERN)

    def set_last_full_state_sync_started_at(self, value: datetime.datetime):
        self.set_state("last_full_state_sync_started_at", str(value))

    def set_last_person_synced_at(self, value: datetime.datetime):
        self.set_state("last_person_synced_at", str(value))

    def set_last_person_for_movies_synced_at(self, value: datetime.datetime):
        self.set_state("last_person_for_movies_synced_at", str(value))

    def set_last_movie_synced_at(self, value: datetime.datetime):
        self.set_state("last_movie_synced_at", str(value))

    def set_last_genre_synced_at(self, value: datetime.datetime):
        self.set_state(f"last_genre_synced_at", str(value))

    def set_last_genre_for_genres_synced_at(self, value: datetime.datetime):
        self.set_state(f"last_genre_for_genres_synced_at", str(value))

    def add_movies_synced(self, movie_ids: List[str]):
        self.set_state("movies_synced", self.movies_synced + tuple(movie_ids))

    def add_genres_for_genres_synced(self, genre_ids: List[str]):
        self.set_state(f"genres_for_genres_synced", self.genres_synced + tuple(genre_ids))

    def add_persons_synced(self, person_ids: List[str]):
        self.set_state("persons_synced", self.persons_synced + tuple(person_ids))

    def complete_full_sync(self):
        """
        Resets updated entities cache - we should sync again all of updated movies since last iteration finish.
        """
        self.set_state("movies_synced", [])
        self.set_state("genres_synced", [])
        self.set_state("persons_synced", [])
