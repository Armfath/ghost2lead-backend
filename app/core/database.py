from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import configs

engine = create_async_engine(
    configs.DATABASE_URL,
    echo=configs.DEBUG,
)

db_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db_transaction() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that commits on success, rolls back on exception."""
    async with db_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


posthog_engine = create_async_engine(
    configs.POSTHOG_DATABASE_URL,
    echo=configs.DEBUG,
)

posthog_db_session_maker = async_sessionmaker(
    posthog_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_posthog_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with posthog_db_session_maker() as session:
        yield session
