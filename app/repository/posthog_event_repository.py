from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.util.enums import EventName, OrderBy


class PostHogEventRepository:
    def __init__(self, session: AsyncSession, project_id: int, table_name: str):
        self.session = session
        self.project_id = project_id
        self.table_name = table_name

    async def get_event(
        self,
        distinct_id: str,
        event_name: EventName | None = None,
        order_by: OrderBy = OrderBy.DESC,
    ) -> dict | None:
        if event_name:
            stmt = text(
                f"""
                SELECT event, properties, timestamp
                FROM {self.table_name}
                WHERE  team_id = :team_id
                  AND distinct_id = :distinct_id
                  AND event = :event_name
                ORDER BY "timestamp" {order_by.value}
                LIMIT 1
                """
            )
            result = await self.session.execute(
                stmt,
                {
                    "team_id": self.project_id,
                    "distinct_id": distinct_id,
                    "event_name": event_name,
                },
            )
            row = result.mappings().first()
        else:
            stmt = text(
                f"""
                SELECT event, properties, timestamp
                FROM {self.table_name}
                WHERE  team_id = :team_id
                  AND distinct_id = :distinct_id
                ORDER BY "timestamp" {order_by.value}
                LIMIT 1
                """
            )
            result = await self.session.execute(
                stmt,
                {
                    "team_id": self.project_id,
                    "distinct_id": distinct_id,
                },
            )
            row = result.mappings().first()
        return dict(row) if row else None

    async def count_by_event(
        self,
        distinct_id: str,
        event_name: EventName,
    ) -> int:
        stmt = text(
            f"""
            SELECT COUNT(*) AS cnt
            FROM {self.table_name}
            WHERE team_id = :team_id
              AND distinct_id = :distinct_id
              AND event = :event_name
            """
        )
        result = await self.session.execute(
            stmt,
            {
                "team_id": self.project_id,
                "distinct_id": distinct_id,
                "event_name": event_name,
            },
        )
        row = result.mappings().first()
        return row["cnt"] if row else 0
