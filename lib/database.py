from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config.settings import app_settings, db_settings

engine = create_async_engine(
    db_settings.DATABASE_URL,
    echo=app_settings.DEBUG,
)

db_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db_session():
    """Dependency for getting database sessions."""
    async with db_session_maker() as session:
        yield session
