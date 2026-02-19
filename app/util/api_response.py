from typing import TypeVar

from app.schemas.base_schema import APISuccess, PaginationInfo, PaginationResponse

T = TypeVar("T")


def to_paginated_success(
    data: list[T],
    total: int,
    page: int,
    page_size: int,
) -> APISuccess[PaginationResponse[T]]:
    return APISuccess(
        data=PaginationResponse(
            items=data,
            pagination=PaginationInfo(
                page=page,
                page_size=page_size,
                total=total,
            ),
        )
    )
