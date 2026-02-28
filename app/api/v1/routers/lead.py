from uuid import UUID

from fastapi import APIRouter

from app.core.dependencies import (
    AdminUserDep,
    CurrentUserDep,
    LeadServiceDep,
    PaginationParamsDep,
)
from app.schemas.base_schema import APISuccess, PaginationResponse
from app.schemas.lead_schema import (
    LeadCreate,
    LeadCreateResponse,
    LeadResponse,
)
from app.util.api_response import to_paginated_success

router = APIRouter(prefix="/leads", tags=["leads"])


@router.post("", response_model=APISuccess[LeadCreateResponse])
async def create_lead(
    data: LeadCreate,
    service: LeadServiceDep,
):
    lead = await service.get_or_create_lead(data)
    return APISuccess(data=lead)


@router.get("", response_model=APISuccess[PaginationResponse[LeadResponse]])
async def get_leads(
    _admin: AdminUserDep,
    service: LeadServiceDep,
    params: PaginationParamsDep,
):
    leads, total = await service.get_list(params.page, params.page_size)
    return to_paginated_success(leads, total, params.page, params.page_size)


@router.get("/{lead_id}", response_model=APISuccess[LeadResponse])
async def get_lead(
    lead_id: UUID,
    current_user: CurrentUserDep,
    service: LeadServiceDep,
):
    lead = await service.get_lead(lead_id, current_user)
    return APISuccess(data=lead)


@router.post("/{lead_id}/enrich", response_model=APISuccess[LeadResponse])
async def enrich_lead(
    lead_id: UUID,
    _admin: AdminUserDep,
    service: LeadServiceDep,
):
    lead = await service.enrich_lead(lead_id)
    return APISuccess(data=lead)
