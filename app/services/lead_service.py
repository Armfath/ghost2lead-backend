from app.models.lead import Lead
from app.repository.lead_repository import LeadRepository
from app.schemas.lead_schema import LeadCreate
from app.services.base_service import BaseService


class LeadService(BaseService[Lead]):
    def __init__(self, lead_repository: LeadRepository):
        super().__init__(lead_repository)

    async def get_or_create_lead(self, schema: LeadCreate):
        if schema.lead_id:
            return await self.get_by_id(schema.lead_id)
        else:
            new_lead = Lead()
            return await self.add(new_lead)
