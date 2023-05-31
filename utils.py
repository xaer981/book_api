from math import ceil

from fastapi import HTTPException, status

from messages import NOT_FOUND_PAGE


def paginator(results: dict, page: int, limit: int) -> tuple[int, dict]:
    """
    Paginate results.

    Args:
        results (dict): results to paginate.
        page (int): requested page.
        limit (int): limit for results per page.

    Raises:
        HTTPException: if page doesn't exist in results.

    Returns:
        tuple[int, dict]: total pages generated, results
    """
    offset_min = (page - 1) * limit
    offset_max = page * limit
    total_pages = ceil(len(results) / limit)

    if page > total_pages:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=NOT_FOUND_PAGE.format(page=page))

    return total_pages, dict(list(results.items())[offset_min:offset_max])
