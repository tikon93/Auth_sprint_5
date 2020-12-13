import backoff
from redis import Redis
from redis.exceptions import ConnectionError

from tests.functional.settings import REDIS_HOST, REDIS_PORT, REDIS_CONNECT_TIMEOUT


@backoff.on_exception(backoff.constant, ConnectionError, interval=REDIS_CONNECT_TIMEOUT)
def ping_redis_until_connection(redis: Redis):
    redis.ping()


if __name__ == '__main__':
    redis = Redis(host=REDIS_HOST, port=REDIS_PORT)
    ping_redis_until_connection(redis)
