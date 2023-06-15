import hashlib

from fastapi import Request, Response
from fastapi_cache import FastAPICache


def custom_key_builder(
    func,
    namespace: str = "",
    request: Request = None,
    response: Response = None,
    args: tuple = None,
    kwargs: dict = None,
) -> str:
    """
    Generating cache key with request.query_params
    to cache paginated results correctly.
    """
    prefix = f'{FastAPICache.get_prefix()}:{namespace}:'
    if 'db' in kwargs:
        del kwargs['db']

    return (prefix
            + hashlib.md5(
                          f'{func.__module__}:{func.__name__}'
                          f':{args}:{kwargs}:{request.query_params}'
                          .encode()).hexdigest())
