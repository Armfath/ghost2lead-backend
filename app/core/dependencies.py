from typing import Annotated, Any
from uuid import UUID

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import configs
from app.core.database import get_db_transaction, get_posthog_db_session
from app.core.redis_client import is_jti_blacklisted
from app.models.user import User
from app.repository.lead_repository import LeadRepository
from app.repository.posthog_event_repository import PostHogEventRepository
from app.repository.user_repository import UserRepository
from app.core.exceptions import ForbiddenError, UnauthorizedError
from app.schemas.base_schema import FindBase
from app.security.oauth2 import oauth2_scheme
from app.security.jwt import decode_token
from app.services.lead_service import LeadService
from app.services.user_service import UserService

# Dependency for getting database transactions.
DBTransactionDep = Annotated[AsyncSession, Depends(get_db_transaction)]

# Dependency for getting PostHog database session.
PostHogDBSessionDep = Annotated[AsyncSession, Depends(get_posthog_db_session)]


# Lead dependencies
def get_lead_repository(session: DBTransactionDep) -> LeadRepository:
    return LeadRepository(session)


# PostHog event repository
def get_posthog_event_repository(
    session: PostHogDBSessionDep,
) -> PostHogEventRepository:
    return PostHogEventRepository(
        session,
        configs.POSTHOG_PROJECT_ID,
        configs.POSTHOG_EVENTS_TABLE_NAME,
    )


def get_lead_service(
    repo: Annotated[LeadRepository, Depends(get_lead_repository)],
    event_repo: Annotated[
        PostHogEventRepository, Depends(get_posthog_event_repository)
    ],
) -> LeadService:
    return LeadService(repo, event_repo)


LeadRepositoryDep = Annotated[LeadRepository, Depends(get_lead_repository)]
LeadServiceDep = Annotated[LeadService, Depends(get_lead_service)]


# Auth dependencies
def get_user_repository(session: DBTransactionDep) -> UserRepository:
    return UserRepository(session)


def get_user_service(
    user_repo: Annotated[UserRepository, Depends(get_user_repository)],
    lead_repo: Annotated[LeadRepository, Depends(get_lead_repository)],
) -> UserService:
    return UserService(user_repo, lead_repo)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]


async def get_user_token(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict[str, Any]:
    token_data = decode_token(token)
    if not token_data:
        raise UnauthorizedError("Invalid token")
    if await is_jti_blacklisted(token_data.get("jti", "")):
        raise UnauthorizedError("Token has been revoked")
    return token_data


async def get_current_user(
    token_data: Annotated[dict[str, Any], Depends(get_user_token)],
    user_repo: UserRepositoryDep,
) -> User:
    user = await user_repo.find_by_id(UUID(token_data["sub"]))
    if not user:
        raise UnauthorizedError("User not found")
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


async def get_admin_user(
    user: CurrentUserDep,
) -> User:
    from app.util.enums import UserType

    if user.user_type != UserType.ADMIN:
        raise ForbiddenError("Admin access required")
    return user


AdminUserDep = Annotated[User, Depends(get_admin_user)]


# Pagination dependencies
def get_pagination_params(
    page: int = Query(configs.PAGE, ge=1),
    page_size: int = Query(
        configs.PAGE_SIZE,
        ge=configs.PAGE_SIZE_MIN,
        le=configs.PAGE_SIZE_MAX,
    ),
) -> FindBase:
    return FindBase(page=page, page_size=page_size)


PaginationParamsDep = Annotated[FindBase, Depends(get_pagination_params)]
