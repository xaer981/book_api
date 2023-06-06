from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Book, Chapter


def get_book_list(db: Session, limit: int = 100):
    """
    Getting list of all books in DB with limit.

    Args:
        db (Session): database session.
        limit (int, optional): Limit for output. Defaults to 100.

    Returns:
        list: books.
    """

    return db.query(Book).limit(limit).all()


def get_book_by_id(db: Session, book_id: int):
    """
    Getting book by number.

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
