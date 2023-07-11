from sqlalchemy import Column, ForeignKey, Integer, String, Text, func, select
from sqlalchemy.orm import column_property, relationship

from .database import Base


class Book(Base):
    """
    Book model.

    Fields:
    id (int) = primary key.
    path (str) = path to book(file name).
    name (str) = name of book.
    chapters = relationship with Chapter model.
    author_id = id of author in Author model.
    author = relationship with Author model.
    """
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, index=True)
    name = Column(String, unique=True, index=True)
    chapters = relationship('Chapter', back_populates='book')
    author_id = Column(Integer, ForeignKey('authors.id'))
    author = relationship('Author', back_populates='books')


class Author(Base):
    """
    Author model.

    Fields:
    id (int) = primary key.
    name (str) = name of author.
    books = relationship with Book model.
    books_count (int) = total books of author.
    """
    __tablename__ = 'authors'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    books = relationship('Book', back_populates='author')
    books_count = column_property(select(func.count(Book.id))
                                  .where(Book.author_id == id)
                                  .correlate_except(Book)
                                  .scalar_subquery())


class Chapter(Base):
    """
    Chapter model.

    Fields:
    id (int) = primary key.
    number (int) = number of chapter in book.
    name (str) = name of chapter.
    text (str) = text of chapter.
    book_id (int) = id of book in Book model.
    book = relationship with Book model.
    """
    __tablename__ = 'chapters'

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=False)
    name = Column(String, unique=False)
    text = Column(Text)
    book_id = Column(Integer, ForeignKey('books.id'))
    book = relationship('Book', back_populates='chapters')
