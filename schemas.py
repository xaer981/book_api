from pydantic import BaseModel


class BookResultOut(BaseModel):
    books: dict[int, str]
    page: int
    limit: int
    total_pages: int


class SearchResultOut(BaseModel):
    book_no: int
    book_name: str
    book_author: str
    results: dict[int, str]
    page: int
    limit: int
    total_pages: int
