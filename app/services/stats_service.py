from datetime import date
from typing import Literal

from app.repository.stats_repository import StatsRepository
from app.schemas.stats_schema import (
    ConfidenceBreakdown,
    EnrichmentStats,
    FunnelStats,
    LeadsSummary,
    LostOpportunities,
    OverTimeStats,
    TimeSeriesPoint,
    DropOffs,
)


class StatsService:
    def __init__(self, repository: StatsRepository):
        self._repository = repository

    async def get_funnel_stats(self) -> FunnelStats:
        row = await self._repository.fetch_funnel_row()

        total_leads = int(row.get("total_leads") or 0)
        signed_up = int(row.get("signed_up") or 0)
        first_actions = int(row.get("first_actions") or 0)
        pricing_views = int(row.get("pricing_views") or 0)

        if total_leads > 0:
            signup_conversion_rate = signed_up / total_leads * 100
            visit_to_signup = 100 - signup_conversion_rate
            visit_to_pricing = pricing_views / total_leads * 100
        else:
            signup_conversion_rate = 0.0
            visit_to_signup = 0.0
            visit_to_pricing = 0.0

        if signed_up > 0:
            signup_to_first_action = (signed_up - first_actions) / signed_up * 100
        else:
            signup_to_first_action = 0.0

        drop_offs = DropOffs(
            visit_to_signup=visit_to_signup,
            signup_to_first_action=signup_to_first_action,
            visit_to_pricing=visit_to_pricing,
        )

        return FunnelStats(
            total_leads=total_leads,
            signed_up=signed_up,
            first_actions=first_actions,
            pricing_views=pricing_views,
            signup_conversion_rate=signup_conversion_rate,
            drop_offs=drop_offs,
        )

    async def get_lost_opportunities(
        self,
        baseline_conversion_rate: float,
    ) -> LostOpportunities:
        row = await self._repository.fetch_lost_opportunities_row()

        total_leads = int(row.get("total_leads") or 0)
        actual_signups = int(row.get("actual_signups") or 0)

        expected = round(total_leads * baseline_conversion_rate)
        lost = max(0, expected - actual_signups)

        return LostOpportunities(
            total_leads=total_leads,
            actual_signups=actual_signups,
            expected_signups_at_baseline=expected,
            lost_signups=lost,
            baseline_used=baseline_conversion_rate,
        )

    async def get_leads_summary(self) -> LeadsSummary:
        row = await self._repository.fetch_leads_summary_row()

        return LeadsSummary(
            total_leads=int(row.get("total_leads") or 0),
            anonymous_leads=int(row.get("anonymous_leads") or 0),
            signed_up_leads=int(row.get("signed_up_leads") or 0),
            enriched_leads=int(row.get("enriched_leads") or 0),
            leads_with_pricing_view=int(row.get("leads_with_pricing_view") or 0),
            pending_enrichment=int(row.get("pending_enrichment") or 0),
        )

    async def get_leads_over_time(
        self,
        granularity: Literal["day", "week"],
        from_date: date,
        to_date: date,
    ) -> OverTimeStats:
        rows = await self._repository.fetch_leads_over_time_rows(
            granularity=granularity,
            from_date=from_date,
            to_date=to_date,
        )

        series: list[TimeSeriesPoint] = []
        for row in rows:
            bucket = row.get("bucket")
            bucket_date_str = bucket.isoformat() if bucket is not None else ""
            series.append(
                TimeSeriesPoint(
                    date=bucket_date_str,
                    new_leads=int(row.get("new_leads") or 0),
                    signups=int(row.get("signups") or 0),
                    pricing_views=int(row.get("pricing_views") or 0),
                    first_actions=int(row.get("first_actions") or 0),
                )
            )

        return OverTimeStats(
            granularity=granularity,
            from_date=from_date.isoformat(),
            to_date=to_date.isoformat(),
            series=series,
        )

    async def get_enrichment_stats(self) -> EnrichmentStats:
        counts_row = await self._repository.fetch_enrichment_counts_row()
        confidence_rows = await self._repository.fetch_confidence_breakdown_rows()

        total_enriched = int(counts_row.get("total_enriched") or 0)
        not_enriched = int(counts_row.get("not_enriched") or 0)

        confidence_counts: dict[str, int] = {
            "High": 0,
            "Medium": 0,
            "Low": 0,
        }
        for row in confidence_rows:
            key = row.get("confidence")
            if key in confidence_counts:
                confidence_counts[key] = int(row.get("count") or 0)

        breakdown = ConfidenceBreakdown(
            High=confidence_counts["High"],
            Medium=confidence_counts["Medium"],
            Low=confidence_counts["Low"],
        )

        return EnrichmentStats(
            total_enriched=total_enriched,
            not_enriched=not_enriched,
            confidence_breakdown=breakdown,
        )

