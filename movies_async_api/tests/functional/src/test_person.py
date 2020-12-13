from http import HTTPStatus
from typing import List, Dict, Tuple, Any

import pytest

from tests.functional.testdata.es_index_data import ES_PERSONS_INDEX_NAME, ES_MOVIES_INDEX_NAME
from tests.functional.testdata import person_samples
from tests.functional.testdata.person_samples import get_expected_person, get_expected_list_person
from tests.functional.testdata.base_samples import get_expected_not_found_details
from tests.functional.utils.api_worker import get_from_api


@pytest.mark.parametrize(
    "es_data_setup",
    [
        [(ES_PERSONS_INDEX_NAME, person_samples.PERSON_SAMPLES_1[0])] +
        [(ES_MOVIES_INDEX_NAME, film) for film in person_samples.RELATED_FILM_SAMPLES_1],
    ],
    indirect=True
)
def test_get_person_details(es_data_setup: List[Tuple[str, Dict[str, Any]]], redis_data_setup):
    person = es_data_setup[0][1]
    films = [entity for index, entity in es_data_setup if index == ES_MOVIES_INDEX_NAME]
    response = get_from_api(f'person/{person["id"]}/')
    assert response == get_expected_person(person, films)


def test_get_empty_film_details(redis_data_setup):
    response = get_from_api(f'person/{person_samples.PERSON_SAMPLES_1[0]["id"]}/',
                            expected_status_code=HTTPStatus.NOT_FOUND)
    assert response == get_expected_not_found_details("person")


@pytest.mark.parametrize(
    "es_data_setup",
    [
        [(ES_PERSONS_INDEX_NAME, person) for person in person_samples.PERSON_SAMPLES_1] +
        [(ES_MOVIES_INDEX_NAME, film) for film in person_samples.RELATED_FILM_SAMPLES_1]
    ],
    indirect=True
)
def test_get_all_persons(es_data_setup: List[Tuple[str, Dict[str, Any]]], redis_data_setup):
    persons = [entity for index, entity in es_data_setup if index == ES_PERSONS_INDEX_NAME]
    response = get_from_api('person/')
    assert response == get_expected_list_person(persons)


@pytest.mark.parametrize(
    "es_data_setup",
    [
        [(ES_PERSONS_INDEX_NAME, person) for person in person_samples.PERSON_SAMPLES_1],
    ],
    indirect=True
)
def test_sort_persons(es_data_setup: List[Tuple[str, Dict[str, Any]]], redis_data_setup):
    persons = [person for index, person in es_data_setup]
    for sort_order in ["asc", "desc"]:
        response = get_from_api('person/', {"sort_order": sort_order})
        assert response == get_expected_list_person(persons, sort_order=sort_order)


@pytest.mark.parametrize(
    "es_data_setup",
    [
        [(ES_PERSONS_INDEX_NAME, person) for person in person_samples.PERSON_SAMPLES_1],
    ],
    indirect=True
)
def test_pagination_persons(es_data_setup: List[Tuple[str, Dict[str, Any]]], redis_data_setup):
    persons = [person for index, person in es_data_setup]
    count_pages = 5
    page_size = len(persons) // count_pages
    if len(persons) % count_pages:
        count_pages += 1
    for page_number in range(1, count_pages + 1):
        response = get_from_api('person', {"page[number]": page_number, "page[size]": page_size})
        assert response == get_expected_list_person(persons, page_number=page_number, page_size=page_size)


@pytest.mark.parametrize(
    "es_data_setup",
    [
        [(ES_PERSONS_INDEX_NAME, person) for person in person_samples.PERSON_SAMPLES_1],
    ],
    indirect=True
)
def test_outside_page_genre(es_data_setup: List[Tuple[str, Dict[str, Any]]], redis_data_setup):
    response = get_from_api('film/', {"page[number]": len(person_samples.PERSON_SAMPLES_1) * 2})
    assert response == []


@pytest.mark.parametrize(
    "redis_data_setup",
    [
        [(f'Person_{person_samples.PERSON_SAMPLES_1[0]["id"]}', person_samples.PERSON_SAMPLES_1[0])]
    ],
    indirect=True
)
def test_cached_person(redis_data_setup: List[Tuple[str, Any]]):
    person_data = redis_data_setup[0][1]
    response = get_from_api(f'person/{person_data["id"]}/')
    assert response == get_expected_person(person_data)
