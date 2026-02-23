from uuid import UUID
from app.models.base import BaseModel
from app.repository.base_repository import BaseRepository
from typing import Generic, TypeVar

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseService(Generic[ModelType]):
    def __init__(self, repository: BaseRepository[ModelType]):
        self._repository = repository

    async def get_by_id(self, id: UUID) -> ModelType:
        return await self._repository.read_by_id(id)

    async def add(self, entity: ModelType) -> ModelType:
        return await self._repository.create(entity)

    async def get_list(self, page: int, page_size: int) -> tuple[list[ModelType], int]:
        return await self._repository.read_list(page, page_size)

    async def patch(self, id: UUID, /, **values: object) -> ModelType:
        return await self._repository.update(id, **values)
