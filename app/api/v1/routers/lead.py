from fastapi import APIRouter

from app.core.dependencies import ClientIPDep, LeadServiceDep
from app.schemas.base_schema import APISuccess
from app.schemas.lead_schema import LeadCreate, LeadCreateResponse

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=APISuccess[LeadCreateResponse])
async def create_lead(
    data: LeadCreate,
    service: LeadServiceDep,
    ip_address: ClientIPDep,
):
    lead = await service.get_or_create_lead(data, ip_address)
    return APISuccess(data=lead)
