from typing import List, Dict, Any, Optional

from tests.functional.testdata.film_samples import get_expected_short_film

DEFAULT_PAGE_SIZE: int = 20
DEFAULT_PAGE_NUMBER: int = 1
DEFAULT_SORT_FIELD: str = "full_name"
DEFAULT_SORT_ORDER: str = "asc"


def get_expected_person(person: Dict[str, Any],
                        related_films: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    if related_films is None:
        related_films = []
    expected_person = {"uuid": person["id"], "full_name": person["full_name"], "roles": {}}
    for role in ["actor", "writer", "director"]:
        expected_person["roles"][role] = []
        for film in related_films:
            if expected_person["full_name"] in [person["name"] for person in film[f"{role}s"]]:
                expected_person["roles"][role].append(get_expected_short_film(film))
    return expected_person


def get_expected_short_person(person: Dict[str, Any]) -> Dict[str, Any]:
    return {"uuid": person["id"], "full_name": person["full_name"]}


def get_expected_list_person(persons: List[Dict[str, Any]],
                             page_size: int = DEFAULT_PAGE_SIZE, page_number: int = DEFAULT_PAGE_NUMBER,
                             sort_field: str = DEFAULT_SORT_FIELD,
                             sort_order: str = DEFAULT_SORT_ORDER) -> List[Dict[str, Any]]:
    expected_list_person = sorted(persons, key=lambda person: person[sort_field], reverse=(sort_order == "desc"))
    expected_list_person = [get_expected_short_person(person) for person in expected_list_person]
    return expected_list_person[(page_number - 1): (page_number - 1) + page_size]


PERSON_ES_DATA_1 = {
    "id": "488d9f93-e547-477e-bc0d-190de4ad4462",
    "full_name": "Harrison Ford"
}
PERSON_ES_DATA_2 = {
    "id": "2b9aaf72-86fa-4e7d-8f97-4d1731e69b7f",
    "full_name": "Mark Hamill"
}

FILM_ES_DATA_1 = {
    "id": "378aa679-5646-4884-bfdd-de299e2c2b5c",
    "imdb_rating": 6.7,
    "genre": [
        {
            "id": "7fbd8d35-7f0d-4141-b6f6-74e9088c366b",
            "name": "Sci-Fi"
        },
        {
            "id": "6135a119-5a44-4269-a4e2-f5bf6a5c8487",
            "name": "Action"
        },
        {
            "id": "c354e2ee-3708-49ec-8497-1b04aa3a7cb7",
            "name": "Adventure"
        },
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
FILM_ES_DATA_2 = {
    "id": "90199510-1cb1-4fca-b75d-01c7590f02da",
    "imdb_rating": 8.7,
    "genre": [
        {
            "id": "7fbd8d35-7f0d-4141-b6f6-74e9088c366b",
            "name": "Sci-Fi"
        },
        {
            "id": "6135a119-5a44-4269-a4e2-f5bf6a5c8487",
            "name": "Action"
        },
        {
            "id": "c354e2ee-3708-49ec-8497-1b04aa3a7cb7",
            "name": "Adventure"
        },
        {
            "id": "edba9556-2c18-46a2-bb5e-f071af502989",
            "name": "Fantasy"
        }
    ],
    "title": "Star Wars: Episode V - The Empire Strikes Back",
    "description": "Luke Skywalker, Han Solo, Princess Leia and Chewbacca face attack by the Imperial forces and its "
                   "AT-AT walkers on the ice planet Hoth. While Han and Leia escape in the Millennium Falcon, "
                   "Luke travels to Dagobah in search of Yoda. Only with the Jedi master's help will Luke survive "
                   "when the dark side of the Force beckons him into the ultimate duel with Darth Vader.",
    "directors_names": [
        "Irvin Kershner"
    ],
    "actors_names": [
        "Harrison Ford",
        "Mark Hamill",
        "Carrie Fisher",
        "Billy Dee Williams"
    ],
    "writers_names": [
        "Leigh Brackett"
    ],
    "actors": [
        {
            "id": "488d9f93-e547-477e-bc0d-190de4ad4462",
            "name": "Harrison Ford"
        },
        {
            "id": "2b9aaf72-86fa-4e7d-8f97-4d1731e69b7f",
            "name": "Mark Hamill"
        },
        {
            "id": "9623439e-7ce2-4855-9b0d-d2db10f60e42",
            "name": "Carrie Fisher"
        },
        {
            "id": "efaad97f-3aa7-4f33-ae97-4326ddc73196",
            "name": "Billy Dee Williams"
        }
    ],
    "writers": [
        {
            "id": "c54e0d2f-8ee9-4e04-8ff6-e92f33dbd183",
            "name": "Leigh Brackett"
        }
    ],
    "directors": [
        {
            "id": "d5e46652-0c3f-4b2a-be2e-6a1d60f89260",
            "name": "Irvin Kershner"
        }
    ]
}

PERSON_SAMPLES_1 = [PERSON_ES_DATA_1, PERSON_ES_DATA_2]
RELATED_FILM_SAMPLES_1 = [FILM_ES_DATA_1, FILM_ES_DATA_2]
