from app.models.lead import Lead
from app.repository.lead_repository import LeadRepository
from app.schemas.lead_schema import LeadCreate
from app.services.base_service import BaseService
from app.util.encrypt_ip import encrypt_ip


class LeadService(BaseService[Lead]):
    def __init__(self, lead_repository: LeadRepository):
        super().__init__(lead_repository)

    async def get_or_create_lead(self, schema: LeadCreate, ip_address: str):
        if schema.lead_id:
            return await self.get_by_id(schema.lead_id)
        else:
            
            encrypted_ip = None
            if ip_address:
                encrypted_ip = encrypt_ip(ip_address)

            new_lead = Lead(ip_address_encrypted=encrypted_ip)
            return await self.add(new_lead)
