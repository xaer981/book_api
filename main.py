import re

from bs4 import BeautifulSoup

# from text2png import text2png


class Engine:
    def __init__(self) -> None:
        self.__books = [f'book/OPS/ch1-{i}.xhtml' for i in range(1, 30)]

    def get_soup(self, book: str) -> BeautifulSoup:
        """
        Принимает string с расположением книги.
        Возвращает BeatifulSoup из содержания этой книги.
        """
        with open(book, 'r', encoding='utf-8') as file:
            return BeautifulSoup(file, 'xml')

    def search_text(self, query: str, scope: str = 'p') -> str | None:
        """
        Принимает на вход поисковый запрос(query)
        и область(scope) возвращаемого текста(необязательно).
        Если scope не задан, то будет возвращено содержание тэга <p>,
        где найден запрос.
        Можно задать scope 'body',
        чтобы получить всё содержание интересующей главы (тэга body).
        """
        for book in self.__books:
            soup = self.get_soup(book)
            if query:
                result = (soup.find(string=re.compile(query, re.I)))
                if result:
                    return result.find_parent(scope).get_text()
        return None


engine = Engine()
query = None
while query != 'stop':
    query = input('Введите запрос:\n')
    print(engine.search_text(query))


# Перейти от find к find_all() ИЛИ ИСПОЛЬЗОВАТЬ FIND_NEXT, FIND_PREVIOUS!!!
# Чтобы можно было переходить к следующему/предидущему запросу
