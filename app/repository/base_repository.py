from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import func, inspect, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.base import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    def __init__(self, model: type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def read_list(self, page: int, page_size: int) -> tuple[list[T], int]:

        query = select(self.model)

        count_stmt = select(func.count()).select_from(query.subquery())
        total_count = await self.session.execute(count_stmt)
        total = total_count.scalar_one()

        stm = (
            query
            .order_by(self.model.created_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )

        result = await self.session.execute(stm)
        data = result.scalars().all()

        return data, total

    async def read_by_id(self, id: UUID) -> T:
        entity = await self.session.get(self.model, id)
        if not entity:
            raise NotFoundError(self.model.__name__, id)
        return entity

    async def find_by_id(self, id: UUID) -> T | None:
        return await self.session.get(self.model, id)

    async def create(self, entity: T) -> T:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def update(self, id: UUID, /, **values: object) -> T:
        existing = await self.read_by_id(id)
        mapper = inspect(self.model)
        updatable = {attr.key for attr in mapper.column_attrs} - {"id", "created_at"}
        for key, value in values.items():
            if key in updatable:
                setattr(existing, key, value)
        await self.session.flush()
        await self.session.refresh(existing)
        return existing
