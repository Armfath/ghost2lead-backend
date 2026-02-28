from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.dependencies import (
    CurrentUserDep,
    UserServiceDep,
    get_user_token,
)
from app.schemas.base_schema import APISuccess
from app.schemas.user_schema import (
    RequestOtpRequest,
    TokenData,
    UserRead,
    UserUpdate,
    VerifyOtpRequest,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/request-otp", response_model=APISuccess[str])
async def request_otp(body: RequestOtpRequest, service: UserServiceDep):
    await service.request_otp(body.email)
    return APISuccess(data="OTP sent to email")


@router.post("/verify-otp", response_model=APISuccess[TokenData])
async def verify_otp(body: VerifyOtpRequest, service: UserServiceDep):
    token = await service.verify_otp(body.email, body.otp, body.lead_id)
    return APISuccess(data=TokenData(access_token=token, token_type="jwt"))


@router.get("/me", response_model=APISuccess[UserRead])
async def get_me(user: CurrentUserDep, service: UserServiceDep):
    return APISuccess(
        data=UserRead(
            id=user.id,
            email=user.email,
            user_type=user.user_type,
            lead_id=user.lead_id,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
    )


@router.patch("/me", response_model=APISuccess[UserRead])
async def update_me(body: UserUpdate, service: UserServiceDep, user: CurrentUserDep):
    updated = await service.update_user(user, body)
    return APISuccess(data=updated)


@router.get("/logout", response_model=APISuccess[str])
async def logout(
    token_data: Annotated[dict, Depends(get_user_token)],
    service: UserServiceDep,
):
    await service.logout(token_data.get("jti", ""))
    return APISuccess(data="Logged out successfully")
