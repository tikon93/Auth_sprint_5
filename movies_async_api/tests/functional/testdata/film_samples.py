from copy import deepcopy
from typing import List, Dict, Any, Optional

DEFAULT_PAGE_SIZE: int = 20
DEFAULT_PAGE_NUMBER: int = 1
DEFAULT_SORT_FIELD: str = "imdb_rating"
DEFAULT_SORT_ORDER: str = "desc"


def get_expected_film(film: Dict[str, Any]) -> Dict[str, Any]:
    expected_film = deepcopy(film)
    expected_film["uuid"] = expected_film.pop("id")
    for genre in expected_film["genre"]:
        genre["uuid"] = genre.pop("id")
    for person_type in ["actors", "writers", "directors"]:
        for person in expected_film[person_type]:
            person["uuid"] = person.pop("id")
            person["full_name"] = person.pop("name")
        expected_film.pop(f"{person_type}_names")
    return expected_film


def get_expected_short_film(film: Dict[str, Any]) -> Dict[str, Any]:
    return {"uuid": film["id"], "title": film["title"], "imdb_rating": film["imdb_rating"]}


def get_expected_list_film(films: List[Dict[str, Any]],
                           page_size: int = DEFAULT_PAGE_SIZE, page_number: int = DEFAULT_PAGE_NUMBER,
                           sort_field: str = DEFAULT_SORT_FIELD,
                           sort_order: str = DEFAULT_SORT_ORDER,
                           filter_by_actor_id: Optional[str] = None,
                           filter_by_writer_id: Optional[str] = None,
                           filter_by_director_id: Optional[str] = None) -> List[Dict[str, Any]]:
    expected_list_film = [
        film for film in films
        if (
                (
                        (filter_by_actor_id is None) or
                        (filter_by_actor_id in [actor["id"] for actor in film["actors"]])
                ) and
                (
                        (filter_by_writer_id is None) or
                        (filter_by_writer_id in [writer["id"] for writer in film["writers"]])
                ) and
                (
                        (filter_by_director_id is None) or
                        (filter_by_director_id in [director["id"] for director in film["directors"]])
                )
        )
    ]
    expected_list_film = sorted(expected_list_film, key=lambda film: film[sort_field], reverse=(sort_order == "desc"))
    expected_list_film = [get_expected_short_film(film) for film in expected_list_film]
    return expected_list_film[(page_number - 1): (page_number - 1) + page_size]


FILM_ES_DATA_1 = {
    "id": "aec4b240-39d4-495c-b303-451097bdaa6d",
    "title": "Star Trek: First Contact",
    "imdb_rating": 7.6,
    "genre": [
        {
            "id": "c354e2ee-3708-49ec-8497-1b04aa3a7cb7",
            "name": "Adventure"
        },
        {
            "id": "7fbd8d35-7f0d-4141-b6f6-74e9088c366b",
            "name": "Sci-Fi"
        },
        {
            "id": "f03b109e-18fc-493a-aa9b-8f79def687e6",
            "name": "Drama"
        },
        {
            "id": "5d13c978-a535-4e58-8f71-8bf84f87f0f2",
            "name": "Thriller"
        },
        {
            "id": "6135a119-5a44-4269-a4e2-f5bf6a5c8487",
            "name": "Action"
        }
    ],
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
    "title": "Star Wars: Episode IX - The Rise of Skywalker",
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
FILM_ES_DATA_3 = {
    "id": "90199510-1cb1-4fca-b75d-01c7590f02da",
    "title": "Star Wars: Episode V - The Empire Strikes Back",
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

RELATED_PERSON_ES_DATA_1 = {
    "id": "488d9f93-e547-477e-bc0d-190de4ad4462",
    "full_name": "Harrison Ford"
}
RELATED_PERSON_ES_DATA_2 = {
    "id": "2b9aaf72-86fa-4e7d-8f97-4d1731e69b7f",
    "full_name": "Mark Hamill"
}

FILM_SAMPLES_1 = [FILM_ES_DATA_1, FILM_ES_DATA_2, FILM_ES_DATA_3]
FILM_SEARCH_SAMPLES_EXPECTED_1 = [
    {
        "uuid": "378aa679-5646-4884-bfdd-de299e2c2b5c",
        "title": "Star Wars: Episode IX - The Rise of Skywalker",
        "imdb_rating": 6.7
    }
]
FILM_SEARCH_QUERY_FOR_SAMPLES_1 = "Rise"

RELATED_PERSON_SAMPLES_1 = [RELATED_PERSON_ES_DATA_1, RELATED_PERSON_ES_DATA_2]
