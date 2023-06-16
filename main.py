import os
from typing import Annotated

import redis.asyncio as redis
import uvicorn
from dotenv import load_dotenv
from fastapi import Body, Depends, FastAPI, HTTPException, Path, status
from fastapi.responses import PlainTextResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from fastapi_pagination import add_pagination
from sqlalchemy.orm import Session

from book_handler.book_process import get_chapter_text, get_search_results
from book_handler.utils import CustomPage
from core.cache import CustomORJsonCoder, custom_key_builder
from core.constants import (NOT_FOUND_AUTHOR_ID, NOT_FOUND_BOOK_ID,
                            NOT_FOUND_CHAPTER_NUMBER, RESPONSES)
from db import crud, models
from db.database import SessionLocal, engine
from schemas import AuthorBooks, AuthorInfo, Book, BookChapters, SearchResults

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
add_pagination(app)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/authors/',
         response_model=CustomPage[AuthorInfo],
         description='Full list of authors in DB with pagination.')
@cache(expire=240)
async def author_list(db: Session = Depends(get_db)):

    return crud.get_author_list(db)


@app.get('/authors/{author_id}',
         response_model=AuthorBooks,
         description='Author by ID.',
         responses={**RESPONSES})
@cache(expire=240,
       coder=CustomORJsonCoder(response_model=AuthorBooks))
async def author_get(author_id: Annotated[int, Path(ge=0)],
                     db: Session = Depends(get_db)):
    author = crud.get_author_by_id(db, author_id=author_id)
    if author is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=NOT_FOUND_AUTHOR_ID.format(
                                author_id=author_id))

    return author


@app.get('/books/',
         response_model=CustomPage[Book],
         description='Full list of books in DB with pagination.')
@cache(expire=240)
async def book_list(db: Session = Depends(get_db)):

    return crud.get_book_list(db)


@app.get('/books/{book_id}',
         response_model=BookChapters,
         description='Book by ID.',
         responses={**RESPONSES})
@cache(expire=240,
       coder=CustomORJsonCoder(response_model=BookChapters))
async def book_get(book_id: Annotated[int, Path(ge=0)],
                   db: Session = Depends(get_db)):
    book = crud.get_book_by_id(db, book_id=book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=NOT_FOUND_BOOK_ID.format(book_id=book_id))

    return book


@app.get('/books/{book_id}/chapter/{chapter_number}',
         response_class=PlainTextResponse,
         description='Chapter text by book_id and chapter_number.',
         responses={**RESPONSES,
                    200: {'content': {'text/plain': {}},
                          'description': 'Returns text of chapter.'}})
@cache(expire=240)
async def chapter_get(book_id: Annotated[int, Path(ge=0)],
                      chapter_number: Annotated[int, Path(ge=0)],
                      db: Session = Depends(get_db)):
    paths = crud.get_paths(db, book_id, chapter_number)
    if paths['book_path'] is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=NOT_FOUND_BOOK_ID.format(book_id=book_id))

    if paths['chapter_path'] is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=NOT_FOUND_CHAPTER_NUMBER.format(
                                book_id=book_id,
                                chapter_number=chapter_number))

    return get_chapter_text(paths)


@app.get('/books/{book_id}/search/',
         response_model=list[SearchResults],
         description='Search query in book by ID.',
         responses={**RESPONSES})
@cache(expire=240)
async def book_search(book_id: Annotated[int, Path(ge=0)],
                      query: Annotated[str, Body(embed=True, min_length=3)],
                      db: Session = Depends(get_db)):
    book_path = crud.get_paths(db, book_id)

    if book_path['book_path'] is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=NOT_FOUND_BOOK_ID.format(book_id=book_id))

    chap_nums_paths = crud.get_chaps_nums_and_paths(db, book_id)

    return get_search_results(query, book_path, chap_nums_paths)


@app.on_event('startup')
async def startup():
    pool = redis.ConnectionPool.from_url(os.getenv('REDIS_URL'),
                                         encoding='utf-8',
                                         decode_responses=True)
    r = redis.Redis(connection_pool=pool)
    FastAPICache.init(RedisBackend(r),
                      prefix='fastapi-cache',
                      key_builder=custom_key_builder)


@app.on_event('shutdown')
async def shutdown():
    r = redis.Redis.from_url(os.getenv('REDIS_URL'))
    await r.flushall()


if __name__ == '__main__':
    uvicorn.run('main:app', reload=False)
