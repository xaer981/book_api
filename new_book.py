from book_handler.add_book import add_to_db, get_book_info

name, author, chapters = get_book_info('latta.epub')
print(add_to_db(name, author, chapters))