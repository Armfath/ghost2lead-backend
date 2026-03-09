from datetime import date, timedelta
from typing import Literal

from fastapi import APIRouter, HTTPException, Query

from app.core.dependencies import AdminUserDep, StatsServiceDep
from app.schemas.base_schema import APISuccess
from app.schemas.stats_schema import (
    EnrichmentStats,
    FunnelStats,
    LeadsSummary,
    LostOpportunities,
    OverTimeStats,
)

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/funnel", response_model=APISuccess[FunnelStats])
async def get_funnel_stats(
    service: StatsServiceDep,
    admin: AdminUserDep,
):
    stats = await service.get_funnel_stats()
    return APISuccess(data=stats)


@router.get("/lost-opportunities", response_model=APISuccess[LostOpportunities])
async def get_lost_opportunities(
    service: StatsServiceDep,
    admin: AdminUserDep,
    baseline_conversion_rate: float = Query(default=0.05, ge=0.0, le=1.0),
):
    stats = await service.get_lost_opportunities(
        baseline_conversion_rate=baseline_conversion_rate,
    )
    return APISuccess(data=stats)


@router.get("/leads/summary", response_model=APISuccess[LeadsSummary])
async def get_leads_summary(
    service: StatsServiceDep,
    admin: AdminUserDep,
):
    stats = await service.get_leads_summary()
    return APISuccess(data=stats)


@router.get("/leads/over-time", response_model=APISuccess[OverTimeStats])
async def get_leads_over_time(
    service: StatsServiceDep,
    admin: AdminUserDep,
    granularity: Literal["day", "week"] = Query(default="day"),
    from_date: date = Query(default_factory=lambda: date.today() - timedelta(days=30)),
    to_date: date = Query(default_factory=date.today),
):
    if from_date > to_date:
        raise HTTPException(
            status_code=422,
            detail="from_date must be before to_date",
        )

    stats = await service.get_leads_over_time(
        granularity=granularity,
        from_date=from_date,
        to_date=to_date,
    )
    return APISuccess(data=stats)


@router.get("/enrichment", response_model=APISuccess[EnrichmentStats])
async def get_enrichment_stats(
    service: StatsServiceDep,
    admin: AdminUserDep,
):
    stats = await service.get_enrichment_stats()
    return APISuccess(data=stats)

