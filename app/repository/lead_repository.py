from app.models.lead import Lead
from app.repository.base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession


class LeadRepository(BaseRepository[Lead]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(Lead, session)
