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
    prefix = f'{FastAPICache.get_prefix()}:{namespace}:'
    if 'db' in kwargs:
        del kwargs['db']

    return (prefix
            + hashlib.md5(
                          f'{func.__module__}:{func.__name__}:{args}:{kwargs}'
                          .encode()).hexdigest())
