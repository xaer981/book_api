import re

from bs4 import BeautifulSoup
from ebooklib import epub


def open_book(book_name: str):
    """
    Opens book by file name.

    Args:
        book_name (str): file name.

    Returns:
        epub.EpubBook: opened book.
    """

    return epub.read_epub(f'book/{book_name}', options={'ignore_ncx': True})


def get_chapter_text(paths: dict) -> str:
    """
    Getting text of chapter by path (xhtml) to it.

    Args:
        paths (dict): only book_path inside.

    Returns:
        str: text of chapter with replaced multiple break-lines with only one.
    """
    book = open_book(paths['book_path'])
    src_id = paths['chapter_path'].split('#')
    chapter = book.get_item_with_href(src_id[0])
    decoded_chap = chapter.get_content().decode('utf-8')
    soup = BeautifulSoup(decoded_chap, 'xml')

    return re.sub(r'\n+', '\n',
                  (soup.find(id=src_id[1]).get_text(separator='\n').strip()))


def get_search_results(query: str,
                       book_path: dict,
                       chaps_nums_and_paths: list):
    """
    Searching in book by query.

    Args:
        query (str): text query for search.
        book_path (dict): path to book (file name).
        chaps_nums_and_paths (list): list of chapters(number, path (xhtml)).

    Returns:
        results (list): (dicts):
                        {chapter_id (int): number of chapter, where searched,
                         results (list): text found in chapter}.
    """
    results = []
    book = open_book(book_path['book_path'])
    for num_path in chaps_nums_and_paths:
        src_id = num_path[1].split('#')
        chapter = book.get_item_with_href(src_id[0])
        decoded_chap = chapter.get_content().decode('utf-8')
        soup = BeautifulSoup(decoded_chap, 'xml')
        result = (soup
                  .find(id=src_id[1])
                  .find_all(name='p',
                            string=re.compile(rf'^(.*?(\b{query}\b)[^$]*)$',
                                              flags=re.I | re.M)))
        if result:
            results.append({'chapter_id': num_path[0],
                            'results': [res.get_text() for res in result]})

    return results
