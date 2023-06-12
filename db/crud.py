from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Author, Book, Chapter


def get_author_list(db: Session):
    """
    Getting paginated list of all authors in DB with.

    Args:
        db (Session): database session.

    Returns:
        list: authors.
    """

    return paginate(db, select(Author).order_by(Author.id))


def get_author_by_id(db: Session, author_id: int):
    """
    Getting author by id.

    Args:
        db (Session): database session.
        author_id (int): id of author in db.

    Returns:
        item: author.
    """

    return db.query(Author).where(Author.id == author_id).first()


def get_book_list(db: Session):
    """
    Getting paginated list of all books in DB.

    Args:
        db (Session): database session.

    Returns:
        list: books.
    """

    return paginate(db, select(Book).order_by(Book.id))


def get_book_by_id(db: Session, book_id: int):
    """
    Getting book by id.

    Args:
        db (Session): database session.
        book_id (int): id of book in db.

    Returns:
        item: book.
    """

    return db.query(Book).where(Book.id == book_id).first()


def get_paths(db: Session, book_id: int, chapter_number: int = None):
    """
    Getting book_path (file name), and chapter_path (xhtml) - optional.

    Args:
        db (Session): database session.
        book_id (int): id of book in db.
        chapter_number (int, optional): number of chapter in db.
                                        Defaults to None.

    Returns:
        dict: {chapter_path (str): xhtml path to chapter - optional,
               book_path (str): path to book (file name)}.
    """
    paths = {}
    if chapter_number is not None:
        paths['chapter_path'] = (db.query(Chapter.path)
                                 .where(Chapter.book_id == book_id,
                                        Chapter.number == chapter_number)
                                 .scalar())

    paths['book_path'] = db.query(Book.path).where(Book.id == book_id).scalar()

    return paths


def get_chaps_nums_and_paths(db: Session, book_id: int):
    """
    Getting chapters number and chapter path by book_id.

    Args:
        db (Session): database session.
        book_id (int): id of book in db.

    Returns:
        list: list with numbers and paths of every chapter of book.
    """

    return db.execute(select(Chapter.number, Chapter.path)
                      .where(Chapter.book_id == book_id)).all()
