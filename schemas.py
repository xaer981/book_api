from pydantic import BaseModel


class Author(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class BookBase(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True


class Book(BookBase):
    author: Author

    class Config:
        orm_mode = True


class Chapter(BaseModel):
    number: int
    name: str

    class Config:
        orm_mode = True


class BookChapters(Book):
    chapters: list[Chapter] = []

    class Config:
        orm_mode = True


class AuthorBooks(Author):
    books: list[BookBase] = []

    class Config:
        orm_mode = True


class SearchResults(BaseModel):
    chapter_id: int
    results: list[str] = []
