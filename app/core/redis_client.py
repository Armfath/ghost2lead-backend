"""Redis clients for OTP storage and token blacklist (separate DBs)."""

from app.core.config import configs

_redis_otp = None
_redis_blacklist = None


def _get_redis_otp():
    global _redis_otp
    if _redis_otp is None:
        from redis.asyncio import Redis

        _redis_otp = Redis(
            host=configs.REDIS_HOST,
            port=configs.REDIS_PORT,
            db=configs.REDIS_DB_OTP,
            decode_responses=True,
        )
    return _redis_otp


def _get_redis_blacklist():
    global _redis_blacklist
    if _redis_blacklist is None:
        from redis.asyncio import Redis

        _redis_blacklist = Redis(
            host=configs.REDIS_HOST,
            port=configs.REDIS_PORT,
            db=configs.REDIS_DB_TOKEN_BLACKLIST,
            decode_responses=True,
        )
    return _redis_blacklist


def _otp_key(email: str) -> str:
    return f"otp:{email}"


async def set_otp(email: str, otp: str) -> None:
    r = _get_redis_otp()
    await r.set(_otp_key(email), otp, ex=configs.OTP_TTL_SECONDS)


async def get_otp(email: str) -> str | None:
    r = _get_redis_otp()
    return await r.get(_otp_key(email))


async def delete_otp(email: str) -> None:
    r = _get_redis_otp()
    await r.delete(_otp_key(email))


async def add_jti_to_blacklist(jti: str) -> None:
    r = _get_redis_blacklist()
    await r.set(jti, "blacklisted")


async def is_jti_blacklisted(jti: str) -> bool:
    r = _get_redis_blacklist()
    return bool(await r.exists(jti))


async def ping_redis() -> bool:
    """Ping Redis to verify connectivity. Used by health checks."""
    try:
        r = _get_redis_otp()
        await r.ping()
        return True
    except Exception:
        return False
