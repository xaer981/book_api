import re
from unicodedata import normalize

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub
from sqlalchemy import exc, exists, insert, select

from app.db.database import SessionLocal
from app.db.models import Author, Book, Chapter


def get_book_content(book_name: str) -> tuple[dict, dict, tuple]:
    """
    Getting book name, author, chapters list from book by file name.

    Args:
        book_name (str): book_name in dir with files.

    Returns:
        book_obj (dict): contains book name.
        author_obj (dict): contains name of author.
        chapters_obj (tuple): contains number of chapter,
                              name, text of chapter.
    """
    try:
        book = epub.read_epub(f'book/{book_name}',
                              options={'ignore_ncx': True})
    except FileNotFoundError as e:

        return f'File not found!\n Error: {e}'

    book_obj = {'name': book.get_metadata('DC', 'title')[0][0]}
    author_obj = {'name': book.get_metadata('DC', 'creator')[0][0]}
    navs = list(book.get_items_of_type(ebooklib.ITEM_NAVIGATION))
    decoded_nav = navs[0].get_content().decode('utf-8')
    decoded_nav = ' '.join(decoded_nav.split())
    soup = BeautifulSoup(decoded_nav, 'xml')
    navlabels = soup.find_all('navLabel')
    labels = [navlabel.text.strip() for navlabel in navlabels]
    paths = [soup.find(string=label)
             .find_parent('navPoint')
             .find('content')['src']
             for label in labels]
    chapters_text = []
    for path in paths:
        src_id = path.split('#')
        chapter = book.get_item_with_href(src_id[0])
        decoded_chap = chapter.get_content().decode('utf-8')
        s = BeautifulSoup(decoded_chap, 'xml')
        chapters_text.append(re.sub(r'\n+', '\n',
                             (s.find(id=src_id[1])
                              .get_text(separator='\n')
                              .strip())))
    chapters_obj = tuple([{'number': num,
                           'name': label,
                           'text': normalize('NFKD', chapters_text[num])}
                         for num, label in enumerate(labels)])

    return book_obj, author_obj, chapters_obj


def add_to_db(book_obj: dict, author_obj: dict, chapters_obj: tuple):
    """
    Adding files to DB.

    Args:
        book_obj (dict): contains book name.
        author_obj (dict): contains name of author.
        chapters_obj (tuple): contains number of chapter,
                              name, text of chapter.

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
