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
