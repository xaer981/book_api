import os
from contextlib import asynccontextmanager
from typing import Annotated

import aiofiles
import redis.asyncio as redis
from dotenv import load_dotenv
from fastapi import (Depends, FastAPI, HTTPException, Path, Query, UploadFile,
                     status)
from fastapi.responses import PlainTextResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from fastapi_pagination import add_pagination
from sqlalchemy import exc
from sqlalchemy.orm import Session

from app.auth_admin import check_admin
from app.book_handler.utils import CustomPage
from app.core.cache import CustomORJsonCoder, custom_key_builder
from app.core.constants import (BAD_FILE_FORMAT, BOOK_ALREADY_EXISTS,
                                NOT_FOUND_AUTHOR_ID, NOT_FOUND_BOOK_ID,
                                NOT_FOUND_CHAPTER_NUMBER, RESPONSES)
from app.db import crud, models
from app.db.database import engine, get_db
from app.new_book import add_new_book
from app.schemas import (AuthorBooks, AuthorInfo, Book, BookChapters,
                         SearchResults)

load_dotenv()

models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Adding pagination, connecting to redis on startup.
    Flushing all in redis on shutdown.
    """
    add_pagination(app)
    pool = redis.ConnectionPool.from_url(os.getenv('REDIS_URL',
                                                   'redis://book_api-redis'),
                                         encoding='utf-8',
                                         decode_responses=True)
    r = redis.Redis(connection_pool=pool)
    FastAPICache.init(RedisBackend(r),
                      prefix='fastapi-cache',
                      key_builder=custom_key_builder)

    yield

    await r.flushall()


app = FastAPI(lifespan=lifespan, title='book_api')


@app.get('/authors/',
         response_model=CustomPage[AuthorInfo],
         description='Full list of authors in DB with pagination.',
         tags=['Authors'])
@cache()
async def author_list(db: Session = Depends(get_db)):

    return crud.get_author_list(db)


@app.get('/authors/{author_id}',
         response_model=AuthorBooks,
         description='Author by ID.',
         tags=['Authors'],
         responses={**RESPONSES})
@cache(coder=CustomORJsonCoder(response_model=AuthorBooks))
async def author_get(author_id: Annotated[int, Path(ge=0)],
                     db: Session = Depends(get_db)):
    author = crud.get_author(db, author_id=author_id)
    if author is None:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=NOT_FOUND_AUTHOR_ID.format(
                                author_id=author_id))

    return author


@app.get('/books/',
         response_model=CustomPage[Book],
         description='Full list of books in DB with pagination.',
         tags=['Books'])
@cache()
async def book_list(db: Session = Depends(get_db)):

    return crud.get_book_list(db)


@app.post('/books/',
          dependencies=[Depends(check_admin)],
          description='Add .epub book to DB (only for admin).',
          tags=['Books'])
async def book_add(book: UploadFile):
    if book.content_type != 'application/epub+zip':

        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=BAD_FILE_FORMAT)

    async with aiofiles.open(f'book/{book.filename}', 'wb') as out_file:
        content = await book.read()

        await out_file.write(content)

    try:
        result = add_new_book(book.filename)
        await redis.Redis.from_url(os.getenv('REDIS_URL')).flushall()

        return result

    except exc.IntegrityError:

        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=BOOK_ALREADY_EXISTS)

    finally:
        os.remove(f'book/{book.filename}')


@app.get('/books/{book_id}',
         response_model=BookChapters,
         description='Book by ID.',
         tags=['Books'],
         responses={**RESPONSES})
@cache(coder=CustomORJsonCoder(response_model=BookChapters))
async def book_get(book_id: Annotated[int, Path(ge=0)],
                   db: Session = Depends(get_db)):
    book = crud.get_book(db, book_id=book_id)
    if book is None:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=NOT_FOUND_BOOK_ID.format(book_id=book_id))

    return book


@app.get('/books/{book_id}/chapter/{chapter_number}',
         response_class=PlainTextResponse,
         description='Chapter text by book_id and chapter_number.',
         tags=['Books'],
         responses={**RESPONSES,
                    200: {'content': {'text/plain': {}},
                          'description': 'Returns text of chapter.'}})
@cache()
async def chapter_get(book_id: Annotated[int, Path(ge=0)],
                      chapter_number: Annotated[int, Path(ge=0)],
                      db: Session = Depends(get_db)):
    if not crud.book_exists(db, book_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=NOT_FOUND_BOOK_ID.format(book_id=book_id))

    chapter = crud.get_chapter_text(db, book_id, chapter_number)

    if not chapter:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=NOT_FOUND_CHAPTER_NUMBER.format(
                                chapter_number=chapter_number,
                                book_id=book_id))

    return chapter


@app.get('/books/{book_id}/search/',
         response_model=list[SearchResults],
         description='Search query in book by ID.',
         tags=['Books'],
         responses={**RESPONSES})
@cache()
async def book_search(book_id: Annotated[int, Path(ge=0)],
                      query: Annotated[str, Query(min_length=3)],
                      db: Session = Depends(get_db)):
    if not crud.book_exists(db, book_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=NOT_FOUND_BOOK_ID.format(book_id=book_id))

    return crud.search_in_book(db, book_id, query)
