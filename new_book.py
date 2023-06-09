from termcolor import colored, cprint

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


if __name__ == '__main__':
    try:
        file_name = input(colored('Enter file name of book to add:',
                                  'black',
                                  'on_white') + '\n\n')
        print('\n' + add_new_book(file_name))

    except KeyboardInterrupt:
        cprint('Exiting...', 'yellow')
