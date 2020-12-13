import logging
import time
from datetime import datetime, timezone

import psycopg2.extras

from src.config import CONFIG
from src.filters import transform_movie_data, transform_genre_data, load_essences, transform_person_data
from src.producers import (
    extract_movies_updated_due_to_person_change,
    extract_movies_updated_due_to_movie_change,
    extract_movies_updated_due_to_genre_change,
    extract_genres_updated_due_to_genre_change,
    extract_updated_persons
)
from src.state import State
from src.utils import ensure_es_index_exists

logger = logging.getLogger(__name__)

if CONFIG.DEBUG:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)


def run_etl_process(state: State):
    """
    Starts to periodically launch all of ETL pipelines.
    """
    ensure_es_index_exists(CONFIG.ELASTIC_URL, CONFIG.ES_MOVIES_INDEX)
    ensure_es_index_exists(CONFIG.ELASTIC_URL, CONFIG.ES_GENRE_INDEX)
    ensure_es_index_exists(CONFIG.ELASTIC_URL, CONFIG.ES_PERSONS_INDEX)

    while True:
        logger.info("Starting full sync")
        started_at = datetime.now(timezone.utc)
        state.set_last_full_state_sync_started_at(started_at)

        movies_loader = load_essences(CONFIG.ES_MOVIES_INDEX)
        movies_transformer = transform_movie_data(movies_loader)
        extract_movies_updated_due_to_genre_change(movies_transformer, state)
        extract_movies_updated_due_to_movie_change(movies_transformer, state)
        extract_movies_updated_due_to_person_change(movies_transformer, state)
        movies_loader.close()

        genres_loader = load_essences(CONFIG.ES_GENRE_INDEX)
        genres_transformer = transform_genre_data(genres_loader)
        extract_genres_updated_due_to_genre_change(genres_transformer, state)
        genres_loader.close()

        load = load_essences(CONFIG.ES_PERSONS_INDEX)
        transform = transform_person_data(load)
        extract_updated_persons(transform, state)
        load.close()

        state.complete_full_sync()
        logger.info("Full sync completed. Sleeping.")
        time.sleep(CONFIG.UPDATES_CHECK_INTERVAL_SEC)


if __name__ == "__main__":
    logger.info("Starting ETL process")
    state = State(f"{CONFIG.ETL_STATE_STORAGE_FOLDER}/state.json")
    psycopg2.extras.register_uuid()
    run_etl_process(state)
