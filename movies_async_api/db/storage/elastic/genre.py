import logging
from enum import Enum
from typing import Dict

from elasticsearch import AsyncElasticsearch

from core.config import ES_GENRE_INDEX
from models.genre import Genre, SortBy
from .base import BaseESStorageGetter

logger = logging.getLogger(__name__)


class GenreESStorageGetter(BaseESStorageGetter):

    def __init__(self, elastic_driver: AsyncElasticsearch):
        super().__init__(elastic_driver=elastic_driver, elastic_index=ES_GENRE_INDEX, model_cls=Genre)

    @property
    def filter_fields(self) -> Dict[Enum, str]:
        return {}  # filtering is not supported currently

    @property
    def sort_values(self) -> Dict[SortBy, str]:
        return {SortBy.NAME: 'name.raw'}
