import re
from math import ceil

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub


def get_search_results(query: str):
    results = []
    book = epub.read_epub('book/latta.epub')
    book_data = {'name': book.get_metadata('DC', 'title')[0][0],
                 'author': book.get_metadata('DC', 'creator')[0][0]}
    strings = list(book.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    strings = [string.get_content().decode('utf-8') for string in strings]
    for string in strings:
        soup = BeautifulSoup(string, 'xml')
        result = soup.find_all(name='p', string=re.compile(query, re.I))
        if result:
            results.append(result)

    return book_data, [i for sub_list in results for i in sub_list]


def process_results_list(book_data: dict, results: list, page: int, size: int):
    offset_min = page * size
    offset_max = (page + 1) * size
    results = [(num, result.get_text())
               for num, result
               in enumerate(results)]

    return {"book_name": book_data['name'],
            "book_author": book_data['author'],
            "results": results[offset_min:offset_max],
            "page": page,
            "size": size,
            "total": ceil(len(results) / size) - 1}


if __name__ == '__main__':
    data, res = get_search_results('дочь')
    final = process_results_list(data, res, 0, 5)

    resules = final['results']
    print(resules)
