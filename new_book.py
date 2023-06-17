from book_handler.add_book import add_to_db, get_book_content


def add_new_book(file_name: str):
    """
    Adding book content to DB (author, name, chapters).

    Args:
        file_name (str): file name of book (.epub).

    Returns:
        str: result of adding to db (success or not).
    """

    name, author, chapters = get_book_content(file_name)

    return add_to_db(name, author, chapters)
