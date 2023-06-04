import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub
from sqlalchemy.orm import Session
from db.models import Author, Book, Chapter


def get_book_info(book_name: str):
    try:
        book = epub.read_epub(f'book/{book_name}')
    except FileNotFoundError as e:

        return e

    name = book.get_metadata('DC', 'title')[0][0]
    author = book.get_metadata('DC', 'creator')[0][0]
    navs = list(book.get_items_of_type(ebooklib.ITEM_NAVIGATION))
    decoded_nav = navs[0].get_content().decode('utf-8')
    decoded_nav = ' '.join(decoded_nav.split())
    soup = BeautifulSoup(decoded_nav, 'xml')
    navlabels = soup.find_all('navLabel')
    labels = [navlabel.text.strip() for navlabel in navlabels]
    chapters = tuple([{'number': num,
                       'name': label,
                       'path': (soup.find(string=label)
                                .find_parent('navPoint')
                                .find('content')['src'])}
                     for num, label in enumerate(labels)])

    return name, author, chapters


def add_to_db(name, author, chapters):
    db_item = Author(name=author)
    db_item.save()

    return db_item


name, author, chapters = get_book_info('latta.epub')
print(add_to_db(name, author, chapters))
