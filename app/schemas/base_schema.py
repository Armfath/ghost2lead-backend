from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel

from app.core.exceptions import ErrorCode

T = TypeVar("T")


class ModelBaseInfo(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime


class APIError(BaseModel):
    success: bool = False
    error: ErrorCode
    message: Any


class APISuccess(BaseModel, Generic[T]):
    success: bool = True
    data: T


class BlankResponse(BaseModel):
    pass
