from sqlalchemy.orm import Session

from .models import Book, Chapter


def get_book_list(db: Session, limit: int = 100):

    return db.query(Book).limit(limit).all()


def get_book_chapters(db: Session, id: int):
    """Need to check sql queries count."""

    return (db.query(Chapter)
            .where(Chapter.book_id == id)
            .order_by(Chapter.number)
            .all())
