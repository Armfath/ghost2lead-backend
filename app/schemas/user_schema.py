from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.util.enums import UserType


class UserBase(BaseModel):
    email: EmailStr


class UserRead(UserBase):
    id: UUID
    user_type: UserType
    lead_id: UUID | None
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    email: EmailStr | None = None


class RequestOtpRequest(BaseModel):
    email: EmailStr


class VerifyOtpRequest(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=1, max_length=10)
    lead_id: UUID  # Required: customers are leads first


class TokenData(BaseModel):
    access_token: str
    token_type: str
