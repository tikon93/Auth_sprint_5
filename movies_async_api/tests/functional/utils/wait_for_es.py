import time

from elasticsearch import Elasticsearch

from tests.functional.settings import ES_HOST, ES_PORT, ES_CONNECT_TIMEOUT


def ping_es_until_connection(es: Elasticsearch):
    while not es.ping():
        time.sleep(ES_CONNECT_TIMEOUT)


if __name__ == '__main__':
    es = Elasticsearch(host=ES_HOST, port=ES_PORT, verify_certs=True)
    ping_es_until_connection(es)
