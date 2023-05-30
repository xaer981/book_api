import re
from math import ceil
from os import listdir

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub
from fastapi import HTTPException, status

from messages import NOT_FOUND_BOOK_NO


def get_search_results(query: str, book_no: int):
    results = []
    books_list = listdir("book")
    if book_no > (len(books_list) - 1):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=NOT_FOUND_BOOK_NO.format(book_no=book_no))

    book = epub.read_epub(f'book/{books_list[book_no]}')
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


def process_results_list(book_data: dict, results: dict, page: int, size: int):
    offset_min = page * size
    offset_max = (page + 1) * size
    results = dict([(num, result.get_text())
                    for num, result
                    in results.items()])

    return {"book_no": book_data['no'],
            "book_name": book_data['name'],
            "book_author": book_data['author'],
            "results": dict(list(results.items())[offset_min:offset_max]),
            "page": page,
            "size": size,
            "total": ceil(len(results) / size) - 1}
