import re
from os import listdir

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub
from fastapi import HTTPException, status

from book_handler.utils import paginator
from core.messages import NOT_FOUND_BOOK_NO


def open_book(book_name: str):

    return epub.read_epub(f'book/{book_name}')


def get_book_data(book: epub.EpubBook):

    return {'name': book.get_metadata('DC', 'title')[0][0],
            'author': book.get_metadata('DC', 'creator')[0][0]}


def get_books_names_and_no(book_no: int) -> tuple[list, int]:
    """
    Checks if book with book_no exists.

    Args:
        book_no (int): number of book from list.

    Raises:
        HTTPException: if book with book_no doesn't exist.

    Returns:
        books_list (list): books names from dir.
        book_no (int): number of book in books_list.
    """
    books_names = listdir("book")

    if book_no > (len(books_names) - 1):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=NOT_FOUND_BOOK_NO.format(book_no=book_no))

    return books_names, book_no


def get_nav_and_make_soup(book: epub.EpubBook,
                          item_type: ebooklib.EXTENSIONS.keys()):
    navs = list(book.get_items_of_type(item_type))
    decoded_nav = navs[0].get_content().decode('utf-8')
    decoded_nav = ' '.join(decoded_nav.split())

    return BeautifulSoup(decoded_nav, 'xml')


def get_book_list(page: int, limit: int) -> dict:
    """
    Returns all existing books.

    Args:
        page (int): requested page.
        limit (int): limit for results per page.

    Returns:
        dict: all books.
    """
    files = listdir('book')
    book_list = {}
    for num, book_name in enumerate(files):
        book = open_book(book_name)
        book_data = get_book_data(book)

        book_list[num] = ('`{name}`, {author}').format(**book_data)

    total_pages, paginated_results = paginator(book_list, page, limit)

    return {'books': paginated_results,
            'page': page,
            'limit': limit,
            'total_pages': total_pages}


def get_book(book_no: int) -> dict:
    """Works fine."""
    books_names, book_no = get_books_names_and_no(book_no)
    book = open_book(books_names[book_no])
    soup = get_nav_and_make_soup(book, ebooklib.ITEM_NAVIGATION)
    navlabels = soup.find_all('navLabel')
    labels = [navlabel.text.strip() for navlabel in navlabels]

    return dict([(num, label) for num, label in enumerate(labels)])


def get_book_chapter(book_no: int, item_id: int) -> str:
    books_names, book_no = get_books_names_and_no(book_no)
    book = open_book(books_names[book_no])
    soup = get_nav_and_make_soup(book, ebooklib.ITEM_NAVIGATION)
    labels = get_book(book_no)
    label = labels[item_id]
    found_label = soup.find(string=label)
    src = found_label.find_parent('navPoint').find('content')['src']
    src_id = src.split('#')
    chapter = book.get_item_with_href(src_id[0])
    decoded_chap = chapter.get_content().decode('utf-8')
    soup2 = BeautifulSoup(decoded_chap, 'xml')

    return soup2.find(id=src_id[1]).get_text()


def get_search_results(query: str, book_no: int) -> tuple[dict]:
    """
    Open book with book_no (epub format)
    (book_no validates in get_books_names_and_no),
    collects info about book name and author,
    making search using BS4.

    Args:
        query (str): search query.
        book_no (int): number of book in list
                       (validates in get_books_names_and_no).

    Returns:
        book_data (dict): info about book number, author and name.
        results (dict): search results with numbers of each result.
    """
    results = []
    books_names, book_no = get_books_names_and_no(book_no)
    book = open_book(books_names[book_no])
    book_data = get_book_data(book)
    book_data['no'] = book_no
    strings = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    strings = [string.get_content().decode('utf-8') for string in strings]
    for string in strings:
        soup = BeautifulSoup(string, 'xml')
        result = soup.find_all(name='p', string=re.compile(query, re.I))
        if result:
            results.append(result)
    results = [i for sub_list in results for i in sub_list]

    return book_data, dict([(num, result)
                            for num, result
                            in enumerate(results)])


def process_results_list(book_data: dict,
                         results: dict,
                         page: int,
                         limit: int) -> dict:
    """
    Makes dict with response.

    Args:
        book_data (dict): info about book number, author and name.
        results (dict): search results from get_search_results.
        page (int): requested page.
        limit (int): limit for results per page.

    Returns:
        response (dict): response with all info.
    """
    results = dict([(num, result.get_text())
                    for num, result
                    in results.items()])
    total_pages, paginated_results = paginator(results, page, limit)

    return {"book_no": book_data['no'],
            "book_name": book_data['name'],
            "book_author": book_data['author'],
            "results": paginated_results,
            "page": page,
            "limit": limit,
            "total_pages": total_pages}
