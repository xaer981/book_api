from typing import Annotated

import uvicorn
from fastapi import Body, Depends, FastAPI, HTTPException, Path, Query, status
from fastapi.responses import PlainTextResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session

from book_handler.book_process import (get_book, get_book_chapter,
                                       get_book_list, get_search_results,
                                       process_results_list)
from core.messages import NOT_FOUND_CHAPTER_ID, NOT_FOUND_QUERY
from db import crud, models
from db.database import SessionLocal, engine
from schemas import BookResultOut, SearchResultOut

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/test/')
async def test(limit: int = 100, db: Session = Depends(get_db)):

    return crud.get_book_list(db, limit=limit)


@app.get('/test1/{id}')
async def test1(id: int, db: Session = Depends(get_db)):

    return crud.get_book_chapters(db, id=id)


@app.get('/books/', response_model=BookResultOut)
@cache(expire=240)
async def book_list(page: int = Query(ge=1, default=1),
                    limit: int = Query(ge=1, le=100, default=5)):

    return get_book_list(page, limit)


@app.get('/books/{book_no}')
@cache(expire=240)
async def book_get(book_no: Annotated[int, Path(ge=0)]):
    """It works."""

    return get_book(book_no)


@app.get('/books/{book_no}/chapter/{item_id}',
         response_class=PlainTextResponse)
@cache(expire=240)
async def get_chapter(book_no: Annotated[int, Path(ge=0)],
                      item_id: Annotated[int, Path(ge=0)]):
    """
    Need to think about ascii and unicode.
    Can't find with non-break space.
    """

    return get_book_chapter(book_no, item_id)


@app.get('/books/{book_no}/search/', response_model=SearchResultOut)
@cache(expire=240)
async def search_book(book_no: Annotated[int, Path(ge=0)],
                      query: Annotated[str, Body(embed=True)],
                      page: int = Query(ge=1, default=1),
                      limit: int = Query(ge=1, le=100, default=5)):

    book_data, results = get_search_results(query, book_no)

    if results:
        return process_results_list(book_data, results, page, limit)

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=NOT_FOUND_QUERY.format(query=query))


@app.get('/books/{book_no}/search/chapter/{item_id}',
         response_class=PlainTextResponse)
@cache(expire=240)
async def get_chapter_from_search(book_no: Annotated[int, Path(ge=0)],
                                  item_id: Annotated[int, Path(ge=0)],
                                  query: Annotated[str, Body(embed=True)]):

    _, result = get_search_results(query, book_no)
    if result:
        if item_id not in result.keys():

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=NOT_FOUND_CHAPTER_ID.format(
                                    item_id=item_id))

        return result.get(item_id).parent.get_text()

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=NOT_FOUND_QUERY.format(query=query))


@app.on_event('startup')
async def startup():
    FastAPICache.init(InMemoryBackend())


if __name__ == '__main__':
    uvicorn.run('main:app', reload=False)
