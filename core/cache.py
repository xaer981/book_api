import hashlib

import orjson
from fastapi import Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi_cache import Coder, FastAPICache


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


class CustomORJsonCoder(Coder):
    """
    Custom encoder receiving response_model
    to correctly cache result made with response_model ORM.
    """
    def __init__(self, response_model) -> None:
        self.response_model = response_model

    def encode(self, value: any) -> bytes:
        return orjson.dumps(
            self.response_model.from_orm(value),
            default=jsonable_encoder,
            option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY,
        )

    @classmethod
    def decode(cls, value: bytes) -> any:
        return orjson.loads(value)
