from functools import wraps


def coroutine(func):
    @wraps(func)
    def inner(*args, **kwargs):
        fn = func(*args, **kwargs)
        if fn is not None:
            next(fn)
            return fn

    return inner
