from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import Author, Book, Chapter


def get_author_list(db: Session):
    """
    Getting paginated list of all authors in DB ordered by id.

    Args:
        db (Session): database session.

    Returns:
        list: authors.
    """

    return paginate(db, select(Author).order_by(Author.id))


def get_author(db: Session, author_id: int):
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
    Getting paginated list of all books in DB ordered by id.

    Args:
        db (Session): database session.

    Returns:
        list: books.
    """

    return paginate(db, select(Book).order_by(Book.id))


def get_book(db: Session, book_id: int):
    """
    Getting book by id.

    Args:
        db (Session): database session.
        book_id (int): id of book in db.

    Returns:
        item: book.
    """

    return db.query(Book).where(Book.id == book_id).first()


def book_exists(db: Session, book_id: int):
    """
    Checks if book with id exists in DB.

    Args:
        db (Session): database session.
        book_id (int): id of book in db.

    Returns:
        int: count of books(0 = doesn't exist, > 1 = exists).
    """

    return db.query(Book).where(Book.id == book_id).count()


def get_chapter_text(db: Session, book_id: int, chapter_number: int):
    """
    Getting text of chapter by id.

    Args:
        db (Session): database session.
        book_id (int): id of book in db.
        chapter_number (int): chapter.number in db.

    Returns:
        tuple: contains one object (text of chapter).
    """

    return db.execute(select(Chapter.text)
                      .where(Chapter.book_id == book_id,
                             Chapter.number == chapter_number)).first()


def search_in_book(db: Session, book_id: int, query: str):
    """
    Searching in book by query. Using tsquery and headline.

    Args:
        db (Session): database session.
        book_id (int): id of book in db.
        query (str): text to search in book.

    Returns:
        list(dict): results of search with chapter number
                    and found results in it.
    """
    query_func = func.phraseto_tsquery(query, postgresql_regconfig='russian')
    results = db.execute(select(Chapter.number, Chapter.text)
                         .where(Chapter.book_id == book_id)
                         .filter(Chapter.text.op('@@')(query_func))).all()
    final = []
    if results:
        res = [(c[0],
                str(
                db.query(func.ts_headline(
                    'russian',
                    c[1],
                    query_func,
                    'MaxFragments=2, '
                    'MaxWords=20, '
                    'StartSel="<<", '
                    'StopSel=">>"'))
                .first()).strip("(',)"))
               for c in results]
        final = [{'chapter_number': result[0],
                  'result': result[1].replace('\\n', '')}
                 for result in res]

    return final
