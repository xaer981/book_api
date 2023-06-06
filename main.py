from typing import Annotated

import uvicorn
from fastapi import Body, Depends, FastAPI, HTTPException, Path, Query, status
from fastapi.responses import PlainTextResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi_cache.decorator import cache
from sqlalchemy.orm import Session

from book_handler.book_process import get_chapter_text, get_search_results
from core.messages import NOT_FOUND_BOOK_ID, NOT_FOUND_CHAPTER_NUMBER
from db import crud, models
from db.database import SessionLocal, engine
from schemas import Book, BookChapters, SearchResults

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/books/', response_model=list[Book])
@cache(expire=240)
async def book_list(limit: int = Query(ge=1, le=100, default=5),
                    db: Session = Depends(get_db)):

    return crud.get_book_list(db, limit=limit)


@app.get('/books/{book_id}', response_model=BookChapters)
@cache(expire=240)
async def book_get(book_id: Annotated[int, Path(ge=0)],
                   db: Session = Depends(get_db)):

    book = crud.get_book_by_id(db, book_id=book_id)
    if book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=NOT_FOUND_BOOK_ID.format(book_id=book_id))

    return book


@app.get('/books/{book_id}/chapter/{chapter_number}',
         response_class=PlainTextResponse)
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


@app.get('/books/{book_id}/search/', response_model=list[SearchResults])
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
    FastAPICache.init(InMemoryBackend())


if __name__ == '__main__':
    uvicorn.run('main:app', reload=False)
