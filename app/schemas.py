from pydantic import BaseModel


class Author(BaseModel):
    """Schema of Author for using in other schemas."""
    id: int
    name: str

    class Config:
        orm_mode = True


class BookBase(BaseModel):
    """Schema of Book for using in other schemas."""
    id: int
    name: str

    class Config:
        orm_mode = True


class Book(BookBase):
    """Schema of Book for using in /books/ endpoint."""
    author: Author

    class Config:
        orm_mode = True


class Chapter(BaseModel):
    """Schema of Chapter for using in other schemas."""
    number: int
    name: str

    class Config:
        orm_mode = True


class BookChapters(Book):
    """Schema of Book for using in /books/{book_id} endpoint."""
    chapters: list[Chapter]

    class Config:
        orm_mode = True


class AuthorInfo(Author):
    """Schema of Author for using in /authors/ endpoint."""
    books_count: int

    class Config:
        orm_mode = True


class AuthorBooks(Author):
    """Schema of Author for using in /authors/{author_id} endpoint."""
    books: list[BookBase]

    class Config:
        orm_mode = True


class SearchResults(BaseModel):
    """
    Schema for displaing search results in /books/{book_id}/search/ endpoint.
    """
    chapter_number: int
    result: str


class Message(BaseModel):
    """Schema for displaing error messages in docs."""
    detail: str
