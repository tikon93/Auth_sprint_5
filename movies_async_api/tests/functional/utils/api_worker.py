import requests
from typing import Optional

from tests.functional.settings import API_URL


def get_from_api(route: str, params: Optional[dict] = None, expected_status_code: int = 200) -> dict:
    if params is None:
        params = {}
    response = requests.get(f'{API_URL}v1/{route}', params=params)
    assert response.status_code == expected_status_code
    return response.json()
