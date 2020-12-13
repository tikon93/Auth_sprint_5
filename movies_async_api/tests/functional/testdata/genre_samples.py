from typing import List, Dict, Any, Optional

from tests.functional.testdata.film_samples import get_expected_short_film


DEFAULT_PAGE_SIZE: int = 20
DEFAULT_PAGE_NUMBER: int = 1
DEFAULT_SORT_FIELD: str = "name"
DEFAULT_SORT_ORDER: str = "asc"


def get_expected_genre(genre: Dict[str, Any],
                       related_films: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    if related_films is None:
        related_films = []
    expected_genre = {"uuid": genre["id"], "name": genre["name"]}
    expected_genre["films"] = [
        get_expected_short_film(film) for film in related_films
        if expected_genre["name"] in [genre["name"] for genre in film["genre"]]
    ]
    return expected_genre


def get_expected_short_genre(genre: Dict[str, Any]) -> Dict[str, Any]:
    return {"uuid": genre["id"], "name": genre["name"]}


def get_expected_list_genre(genres: List[Dict[str, Any]],
                            page_size: int = DEFAULT_PAGE_SIZE, page_number: int = DEFAULT_PAGE_NUMBER,
                            sort_field: str = DEFAULT_SORT_FIELD,
                            sort_order: str = DEFAULT_SORT_ORDER) -> List[Dict[str, Any]]:
    expected_list_genre = sorted(genres, key=lambda genre: genre[sort_field], reverse=(sort_order == "desc"))
    expected_list_genre = [get_expected_short_genre(genre) for genre in expected_list_genre]
    return expected_list_genre[(page_number - 1): (page_number - 1) + page_size]


GENRE_ES_DATA_1 = {
    "id": "edba9556-2c18-46a2-bb5e-f071af502989",
    "name": "Fantasy",
    "description": None
}
GENRE_ES_DATA_2 = {
    "id": "7fbd8d35-7f0d-4141-b6f6-74e9088c366b",
    "name": "Sci-Fi",
    "description": None
}

FILM_ES_DATA_1 = {
    "id": "aec4b240-39d4-495c-b303-451097bdaa6d",
    "imdb_rating": 7.6,
    "genre": [
        {
            "id": "7fbd8d35-7f0d-4141-b6f6-74e9088c366b",
            "name": "Sci-Fi"
        }
    ],
    "title": "Star Trek: First Contact",
    "description": "In the 24th century, the crew of the Enterprise-E has been ordered to patrol the Romulan Neutral "
                   "Zone by the Federation to avoid interference with their battle against the insidious Borg. "
                   "Witnessing the loss of the battle, Captain Jean-Luc Picard ignores orders and takes command of "
                   "the fleet engaging the Borg. But the Borg plan to travel back into the 21st century through a "
                   "vortex with the intention to stop Earth's first contact with an alien race (the Vulcans). "
                   "Following the Borg sphere, Picard and his crew realize that they have taken over the Enterprise "
                   "in order to carry out their mission. Their only chance to do away with the Borg and their "
                   "seductive queen is to make sure that Zefram Cochrane makes his famous faster-than-light travel "
                   "to the stars.",
    "directors_names": [
        "Jonathan Frakes"
    ],
    "actors_names": [
        "Brent Spiner",
        "LeVar Burton",
        "Patrick Stewart",
        "Jonathan Frakes"
    ],
    "writers_names": [
        "Gene Roddenberry"
    ],
    "actors": [
        {
            "id": "fb04f296-2240-4f94-9c83-518a413c3ee9",
            "name": "Brent Spiner"
        },
        {
            "id": "cfe6b5c1-8f75-448b-a70e-d94956b89d39",
            "name": "LeVar Burton"
        },
        {
            "id": "ff42a473-d1d7-477a-b1b1-48c629a97814",
            "name": "Patrick Stewart"
        },
        {
            "id": "33ca493b-0201-4df4-a8e9-3cdf445b3477",
            "name": "Jonathan Frakes"
        }
    ],
    "writers": [
        {
            "id": "9e0e32dd-d5b3-4ef9-a8bc-0ea63682a380",
            "name": "Gene Roddenberry"
        }
    ],
    "directors": [
        {
            "id": "33ca493b-0201-4df4-a8e9-3cdf445b3477",
            "name": "Jonathan Frakes"
        }
    ]
}
FILM_ES_DATA_2 = {
    "id": "378aa679-5646-4884-bfdd-de299e2c2b5c",
    "imdb_rating": 6.7,
    "genre": [
        {
            "id": "edba9556-2c18-46a2-bb5e-f071af502989",
            "name": "Fantasy"
        }
    ],
    "title": "Star Wars: Episode IX - The Rise of Skywalker",
    "description": "The surviving members of the resistance face the First Order once again, and the legendary "
                   "conflict between the Jedi and the Sith reaches its peak bringing the Skywalker saga to its end.",
    "directors_names": [
        "J.J. Abrams"
    ],
    "actors_names": [
        "Mark Hamill",
        "Adam Driver",
        "Carrie Fisher",
        "Daisy Ridley"
    ],
    "writers_names": [
        "Chris Terrio"
    ],
    "actors": [
        {
            "id": "2b9aaf72-86fa-4e7d-8f97-4d1731e69b7f",
            "name": "Mark Hamill"
        },
        {
            "id": "876dd623-ab44-4c12-b2d3-bec99ed417fe",
            "name": "Adam Driver"
        },
        {
            "id": "9623439e-7ce2-4855-9b0d-d2db10f60e42",
            "name": "Carrie Fisher"
        },
        {
            "id": "5e4f1319-d8d4-42bf-8c9a-22b7a431034e",
            "name": "Daisy Ridley"
        }
    ],
    "writers": [
        {
            "id": "d89f7beb-fa49-4f4f-a0a7-1f0066be5f78",
            "name": "Chris Terrio"
        }
    ],
    "directors": [
        {
            "id": "5b48ff69-3e4b-4f1f-a1e7-8b015cf94be2",
            "name": "J.J. Abrams"
        }
    ]
}

GENRE_SAMPLES_1 = [GENRE_ES_DATA_1, GENRE_ES_DATA_2]
RELATED_FILM_SAMPLES_1 = [FILM_ES_DATA_1, FILM_ES_DATA_2]
