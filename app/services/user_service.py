import random
import string

from uuid import UUID

from app.core.config import configs
from app.core.exceptions import BadRequestError, UnauthorizedError
from app.core.redis_client import add_jti_to_blacklist, delete_otp, get_otp, set_otp
from app.models.user import User
from app.repository.lead_repository import LeadRepository
from app.repository.user_repository import UserRepository
from app.util.enums import UserType
from app.schemas.user_schema import UserRead, UserUpdate
from app.security.jwt import generate_token
from app.services.base_service import BaseService
from app.worker.tasks import send_otp_email


def _generate_otp() -> str:
    return "".join(
        random.choices(string.digits, k=configs.OTP_LENGTH)
    )


class UserService(BaseService[User]):
    def __init__(self, user_repository: UserRepository, lead_repository: LeadRepository):
        self._user_repository = user_repository
        self._lead_repository = lead_repository
        super().__init__(user_repository)

    async def request_otp(self, email: str) -> None:
        otp = _generate_otp()
        await set_otp(email, otp)
        send_otp_email.delay(email, otp)

    async def verify_otp(self, email: str, otp: str, lead_id: UUID) -> str:
        stored = await get_otp(email)
        if not stored or stored != otp:
            raise UnauthorizedError("Invalid or expired OTP")
        await delete_otp(email)

        user = await self._user_repository.get_by_email(email)
        if not user:
            lead = await self._lead_repository.read_by_id(lead_id)  # ensure lead exists
            user = User(
                email=email,
                user_type=UserType.CUSTOMER,
                lead=lead,
            )
            user = await self._user_repository.create(user)

        return generate_token(data={"sub": str(user.id)})

    async def update_user(self, user: User, data: UserUpdate) -> UserRead:
        if data.email is not None:
            existing = await self._user_repository.get_by_email(data.email)
            if existing and existing.id != user.id:
                raise BadRequestError("Email already used")
        updates = data.model_dump(exclude_unset=True)
        if updates:
            updated = await self._user_repository.update(user.id, **updates)
            return self._to_read(updated)
        return self._to_read(user)

    async def logout(self, jti: str) -> None:
        if jti:
            await add_jti_to_blacklist(jti)

    def _to_read(self, user: User) -> UserRead:
        return UserRead(
            id=user.id,
            email=user.email,
            user_type=user.user_type,
            lead_id=user.lead_id,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
