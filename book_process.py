import re
from os import listdir

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub
from fastapi import HTTPException, status

from messages import NOT_FOUND_BOOK_NO
from utils import paginator


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
    for num, file in enumerate(files):
        book = epub.read_epub(f'book/{file}')
        name = book.get_metadata('DC', 'title')[0][0]
        author = book.get_metadata('DC', 'creator')[0][0]

        book_list[num] = f'`{name}`, {author}'

    total_pages, paginated_results = paginator(book_list, page, limit)

    return {'books': paginated_results,
            'page': page,
            'limit': limit,
            'total_pages': total_pages}


def get_book(book_no: int) -> dict:
    """Works better. Can't wind with non-break space!!!"""
    books_names, book_no = get_books_names_and_no(book_no)
    book = epub.read_epub(f'book/{books_names[book_no]}')
    book_nav = list(book.get_items_of_type(ebooklib.ITEM_NAVIGATION))
    decoded_nav = book_nav[0].get_content().decode('utf-8')
    soup = BeautifulSoup(decoded_nav, 'xml')
    navlabels = soup.find_all('navLabel')
    labels = [' '.join(navlabel.text.split()) for navlabel in navlabels]

    return dict([(num, label) for num, label in enumerate(labels)])


def get_book_chapter(book_no: int, item_id: int) -> str:
    books_names, book_no = get_books_names_and_no(book_no)
    book = epub.read_epub(f'book/{books_names[book_no]}')
    book_nav = list(book.get_items_of_type(ebooklib.ITEM_NAVIGATION))
    decoded_nav = book_nav[0].get_content().decode('utf-8')
    soup = BeautifulSoup(decoded_nav, 'xml')
    labels = get_book(book_no)
    label = labels[item_id]
    found_label = soup.find(string=label)
    print(found_label)
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
    book = epub.read_epub(f'book/{books_names[book_no]}')
    book_data = {'no': book_no,
                 'name': book.get_metadata('DC', 'title')[0][0],
                 'author': book.get_metadata('DC', 'creator')[0][0]}
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
