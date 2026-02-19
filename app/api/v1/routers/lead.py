from fastapi import APIRouter

from app.util.api_response import to_paginated_success
from app.core.dependencies import ClientIPDep, LeadServiceDep, PaginationParamsDep
from app.schemas.base_schema import APISuccess, PaginationResponse
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


@router.get("", response_model=APISuccess[PaginationResponse[LeadCreateResponse]])
async def get_leads(
    service: LeadServiceDep,
    params: PaginationParamsDep,
):
    leads, total = await service.get_list(params.page, params.page_size)
    return to_paginated_success(leads, total, params.page, params.page_size)
