from typing import Annotated

from fastapi import Body, FastAPI, Query
from pydantic import BaseModel

from book_process import get_search_results, process_results_list

app = FastAPI()


class ResultOut(BaseModel):
    book_name: str
    book_author: str
    results: list[set]
    page: int
    size: int
    total: int


@app.get('/', response_model=ResultOut | str)
def search_book(query: Annotated[str, Body(embed=True)],
                page: int = Query(ge=0, default=0),
                size: int = Query(ge=1, le=100, default=5)) -> dict | str:

    book_data, results = get_search_results(query)
    if results:
        return process_results_list(book_data, results, page, size)

    return 'Не найдено'
