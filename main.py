from typing import Annotated

import uvicorn
from fastapi import Body, FastAPI, HTTPException, Query, status
from fastapi.responses import PlainTextResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from pydantic import BaseModel

from book_process import get_search_results, process_results_list
from messages import NOT_FOUND, NOT_FOUND_ID

app = FastAPI()


class ResultOut(BaseModel):
    book_name: str
    book_author: str
    results: dict[int, str]
    page: int
    size: int
    total: int


@app.get('/', response_model=ResultOut)
@cache(expire=240)
async def search_book(query: Annotated[str, Body(embed=True)],
                      page: int = Query(ge=0, default=0),
                      size: int = Query(ge=1, le=100, default=5)):

    book_data, results = get_search_results(query)

    if results:
        return process_results_list(book_data, results, page, size)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=NOT_FOUND.format(query=query))


@app.get('/get_chapter/{item_id}', response_class=PlainTextResponse)
@cache(expire=240)
async def get_chapter(query: Annotated[str, Body(embed=True)],
                      item_id: int):

    _, result = get_search_results(query)
    if result:
        if item_id not in result.keys():

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=NOT_FOUND_ID.format(item_id=item_id))

        return result.get(item_id).parent.get_text()

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=NOT_FOUND.format(query=query))


@app.on_event('startup')
async def startup():
    FastAPICache.init(InMemoryBackend())


if __name__ == '__main__':
    uvicorn.run('main:app', reload=False)
