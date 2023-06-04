from sqlalchemy.orm import Session

from .models import Book


def get_book_list(db: Session, limit: int = 100):

    return db.query(Book).limit(limit).all()


def get_book_by_id(db: Session, id: int):

    return db.query(Book).filter(Book.id == id).first()


def get_book_chapters(db: Session, id: int):

    return db.get(Book, id).author
