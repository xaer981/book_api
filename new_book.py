from book_handler.add_book import add_to_db, get_book_info

file_name = input('Введите название файла книги для загрузки.\n')
name, author, chapters = get_book_info(file_name)

print(add_to_db(name, author, chapters))
