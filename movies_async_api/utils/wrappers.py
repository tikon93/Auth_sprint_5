import logging
from typing import Tuple, Type

logger = logging.getLogger(__name__)


def reraise_backoff_exceptions(exceptions_to_catch: Tuple[Type[BaseException], ...],
                               exception_to_raise: Type[Exception]):
    def wrap(func):
        async def wrapped(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except exceptions_to_catch as e:
                logger.error(f"Raising exception to be backed off due to:{type(e)} {str(e)}")
                raise exception_to_raise(repr(e))

        return wrapped

    return wrap
