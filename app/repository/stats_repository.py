from datetime import date

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class StatsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def fetch_funnel_row(self) -> dict:
        stmt = text(
            """
            SELECT
              COUNT(*) AS total_leads,
              COUNT(*) FILTER (
                WHERE (l.behaviors->>'signed_up_at') IS NOT NULL
              ) AS signed_up,
              COUNT(*) FILTER (
                WHERE (l.behaviors->>'exported_file_at') IS NOT NULL
              ) AS first_actions,
              COUNT(*) FILTER (
                WHERE COALESCE((l.behaviors->>'viewed_pricing')::int, 0) > 0
              ) AS pricing_views
            FROM leads l
            """
        )
        result = await self.session.execute(stmt)
        row = result.mappings().one()
        return dict(row)

    async def fetch_lost_opportunities_row(self) -> dict:
        stmt = text(
            """
            SELECT
              COUNT(*) AS total_leads,
              COUNT(*) FILTER (
                WHERE (l.behaviors->>'signed_up_at') IS NOT NULL
              ) AS actual_signups
            FROM leads l
            """
        )
        result = await self.session.execute(stmt)
        row = result.mappings().one()
        return dict(row)

    async def fetch_leads_summary_row(self) -> dict:
        stmt = text(
            """
            SELECT
              COUNT(*) AS total_leads,
              COUNT(*) FILTER (
                WHERE (l.behaviors->>'signed_up_at') IS NULL
              ) AS anonymous_leads,
              COUNT(*) FILTER (
                WHERE (l.behaviors->>'signed_up_at') IS NOT NULL
              ) AS signed_up_leads,
              COUNT(*) FILTER (
                WHERE l.enriched_at IS NOT NULL
              ) AS enriched_leads,
              COUNT(*) FILTER (
                WHERE l.enriched_at IS NULL
              ) AS pending_enrichment,
              COUNT(*) FILTER (
                WHERE COALESCE((l.behaviors->>'viewed_pricing')::int, 0) > 0
              ) AS leads_with_pricing_view
            FROM leads l
            """
        )
        result = await self.session.execute(stmt)
        row = result.mappings().one()
        return dict(row)

    async def fetch_leads_over_time_rows(
        self,
        granularity: str,
        from_date: date,
        to_date: date,
    ) -> list[dict]:
        stmt = text(
            """
            SELECT
              DATE_TRUNC(:granularity, l.created_at)::date AS bucket,
              COUNT(*) AS new_leads,
              COUNT(*) FILTER (
                WHERE (l.behaviors->>'signed_up_at') IS NOT NULL
                  AND DATE_TRUNC(
                        :granularity,
                        (l.behaviors->>'signed_up_at')::timestamptz
                      ) = DATE_TRUNC(:granularity, l.created_at)
              ) AS signups,
              COUNT(*) FILTER (
                WHERE COALESCE((l.behaviors->>'viewed_pricing')::int, 0) > 0
              ) AS pricing_views,
              COUNT(*) FILTER (
                WHERE (l.behaviors->>'exported_file_at') IS NOT NULL
                  AND DATE_TRUNC(
                        :granularity,
                        (l.behaviors->>'exported_file_at')::timestamptz
                      ) = DATE_TRUNC(:granularity, l.created_at)
              ) AS first_actions
            FROM leads l
            WHERE l.created_at BETWEEN :from_date AND :to_date
            GROUP BY bucket
            ORDER BY bucket ASC
            """
        )
        result = await self.session.execute(
            stmt,
            {
                "granularity": granularity,
                "from_date": from_date,
                "to_date": to_date,
            },
        )
        rows = result.mappings().all()
        return [dict(row) for row in rows]

    async def fetch_enrichment_counts_row(self) -> dict:
        stmt = text(
            """
            SELECT
              COUNT(*) FILTER (WHERE l.enriched_at IS NOT NULL) AS total_enriched,
              COUNT(*) FILTER (WHERE l.enriched_at IS NULL) AS not_enriched
            FROM leads l
            """
        )
        result = await self.session.execute(stmt)
        row = result.mappings().one()
        return dict(row)

    async def fetch_confidence_breakdown_rows(self) -> list[dict]:
        stmt = text(
            """
            SELECT
              l.profile->>'confidence' AS confidence,
              COUNT(*) AS count
            FROM leads l
            WHERE l.enriched_at IS NOT NULL
              AND l.profile->>'confidence' IS NOT NULL
            GROUP BY l.profile->>'confidence'
            """
        )
        result = await self.session.execute(stmt)
        rows = result.mappings().all()
        return [dict(row) for row in rows]

