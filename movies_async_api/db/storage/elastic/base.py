import logging
from abc import abstractmethod
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from elasticsearch.exceptions import ConnectionError, ConnectionTimeout, TransportError
from elasticsearch.exceptions import NotFoundError

from db.storage.abstract import AbstractStorageGetter, StorageBackoffException
from models.base import ModelType, SortOrder
from utils.wrappers import reraise_backoff_exceptions

logger = logging.getLogger(__name__)

ES_EXCEPTIONS_TO_BACKOFF = (ConnectionRefusedError, ConnectionError, ConnectionTimeout, TransportError)


class ESStorage:
    def __init__(self, elastic_driver: AsyncElasticsearch, elastic_index: str, model_cls: Any):
        self.driver: AsyncElasticsearch = elastic_driver
        self.elastic_index: str = elastic_index
        self.model_cls = model_cls

    @reraise_backoff_exceptions(exceptions_to_catch=ES_EXCEPTIONS_TO_BACKOFF,
                                exception_to_raise=StorageBackoffException)
    async def _perform_query(
            self,
            page: int,
            per_page: int,
            sort: list,
            query: Optional[dict] = None
    ) -> List[ModelType]:

        query_body = {
            "from": self._get_from(page, per_page),
            "size": per_page,
            "sort": sort
        }
        if query:
            query_body['query'] = query

        results = await self.driver.search(body=query_body, index=self.elastic_index)
        data = results["hits"]["hits"]
        logger.debug(f"Got {len(data)} entities")
        return [self.model_cls(**entity["_source"]) for entity in data]

    @staticmethod
    def _get_from(page: int, per_page: int) -> int:
        return (page - 1) * per_page


class BaseESStorageGetter(AbstractStorageGetter, ESStorage):

    sort_order_values: Dict[Enum, str] = {SortOrder.ASC: "asc", SortOrder.DESC: "desc"}

    def __init__(self, elastic_driver: AsyncElasticsearch, elastic_index: str, model_cls: Any):
        super().__init__(elastic_driver=elastic_driver, elastic_index=elastic_index, model_cls=model_cls)

    @property
    @abstractmethod
    def filter_fields(self) -> Dict[Enum, str]:
        """
        All classes inherited from BaseESStorageGetter must provide fields which support filtering
        """
        pass

    @property
    @abstractmethod
    def sort_values(self) -> Dict[Enum, str]:
        """
        All classes inherited from BaseESStorageGetter must provide fields which support sorting
        """
        pass

    @reraise_backoff_exceptions(exceptions_to_catch=ES_EXCEPTIONS_TO_BACKOFF,
                                exception_to_raise=StorageBackoffException)
    async def get_entity(self, entity_id: UUID, **kwargs) -> ModelType:
        logger.debug(f"Looking for entity with id {entity_id} in ES in index {self.elastic_index}")
        try:
            entity = await self.driver.get(self.elastic_index, str(entity_id))
            return self.model_cls(**entity['_source'])
        except NotFoundError:
            logger.debug(f"Entity {entity_id} not found in {self.elastic_index}")

    async def get_entities(
            self,
            page: int,
            per_page: int,
            sort_by: Optional[Enum] = None,
            sort_order: SortOrder = SortOrder.ASC,
            filters: Optional[Dict[Enum, UUID]] = None,
            logical_and_between_filters: bool = True
    ) -> List[ModelType]:
        logger.debug(f"Getting all entities from index {self.elastic_index}")

        sort = self._get_sort_list_from_sort_inputs(sort_by=sort_by, sort_order=sort_order)

        if filters:
            logger.debug("Building query for filters")
            operand = "must" if logical_and_between_filters else "should"
            query = {'bool': {operand: []}}
            for field_name, value in filters.items():
                if (filter_by := self.filter_fields.get(field_name)) is not None:
                    subquery = {
                        "nested": {"path": filter_by, "query": {"bool": {"must": [
                            {"match": {f"{filter_by}.id": value}}]}}}
                    }
                    query['bool'][operand].append(subquery)
                else:
                    raise ValueError(f"Unsupported field name in filters {field_name}")
        else:
            query = {}

        return await self._perform_query(page=page, per_page=per_page, sort=sort, query=query)

    def _get_sort_list_from_sort_inputs(self, sort_by: Optional[Enum], sort_order: SortOrder) -> list:
        if sort_by is None:
            sort = []
        elif (sort_value := self.sort_values.get(sort_by)) is None:
            raise ValueError(f"Unknown sort field {sort_by}")
        else:
            sort = [{sort_value: self.sort_order_values[sort_order]}]

        return sort
