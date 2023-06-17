import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub
from sqlalchemy import exc, exists, insert, select

from db.database import SessionLocal
from db.models import Author, Book, Chapter


def get_book_content(book_name: str):
    """
    Getting book name, author, chapters list from book by file name.

    Args:
        book_name (str): book_name in dir with files.

    Returns:
        book_obj (dict): contains book name and path (file name).
        author_obj (dict): contains name of author.
        chapters_obj (dict): contains number of chapter,
                             name, path to chapter (href in xhtml).
    """
    try:
        book = epub.read_epub(f'book/{book_name}',
                              options={'ignore_ncx': True})
    except FileNotFoundError as e:

        return f'Файл не найден!\n Ошибка: {e}'

    book_obj = {'name': book.get_metadata('DC', 'title')[0][0],
                'path': book_name}
    author_obj = {'name': book.get_metadata('DC', 'creator')[0][0]}
    navs = list(book.get_items_of_type(ebooklib.ITEM_NAVIGATION))
    decoded_nav = navs[0].get_content().decode('utf-8')
    decoded_nav = ' '.join(decoded_nav.split())
    soup = BeautifulSoup(decoded_nav, 'xml')
    navlabels = soup.find_all('navLabel')
    labels = [navlabel.text.strip() for navlabel in navlabels]
    chapters_obj = tuple([{'number': num,
                           'name': label,
                           'path': (soup.find(string=label)
                                    .find_parent('navPoint')
                                    .find('content')['src'])}
                         for num, label in enumerate(labels)])

    return book_obj, author_obj, chapters_obj


def add_to_db(book_obj, author_obj, chapters_obj):
    """
    Adding files to DB.

    Args:
        book_obj (dict): contains book name and path (file name).
        author_obj (dict): contains name of author.
        chapters_obj (dict): contains number of chapter,
                             name, path to chapter (href in xhtml).

    Returns:
        str: 'Success'
    """
    session = SessionLocal()
    if session.query(exists()
                     .where(Author.name == author_obj['name'])).scalar():
        author_id = session.scalar(select(Author.id)
                                   .where(Author.name == author_obj['name']))
    else:
        author_id = session.scalar(insert(Author)
                                   .returning(Author.id), author_obj)

    book_obj['author_id'] = author_id
    try:
        book_id = session.scalar(insert(Book).returning(Book.id), book_obj)
        session.scalar(insert(Chapter).values(book_id=book_id), chapters_obj)

        session.commit()
        session.close()
    except exc.IntegrityError as e:
        session.rollback()

        raise e

    return 'Success'
