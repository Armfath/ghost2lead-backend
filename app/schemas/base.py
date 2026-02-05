from typing import Any, Generic, TypeVar

from pydantic import BaseModel

from app.core.exceptions import ErrorCode

T = TypeVar("T")


class APIError(BaseModel):
    success: bool = False
    error: ErrorCode
    message: Any

class APISuccess(BaseModel, Generic[T]):
    success: bool = True
    data: T
