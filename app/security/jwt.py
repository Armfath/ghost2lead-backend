from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import uuid4

import jwt

from app.core.config import configs
from app.core.exceptions import UnauthorizedError


def decode_token(token: str) -> dict[str, Any] | None:
    try:
        data = jwt.decode(
            jwt=token,
            key=configs.JWT_SECRET,
            algorithms=[configs.JWT_ALGO],
        )
        return data
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Token expired")
    except jwt.PyJWTError:
        return None


def generate_token(
    data: dict[str, Any],
    expire_days: int | None = None,
) -> str:
    if expire_days is None:
        expire_days = configs.JWT_EXPIRE_DAYS
    return jwt.encode(
        payload={
            **data,
            "jti": str(uuid4()),
            "exp": datetime.now(timezone.utc) + timedelta(days=expire_days),
        },
        key=configs.JWT_SECRET,
        algorithm=configs.JWT_ALGO,
    )
