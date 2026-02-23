from uuid import UUID

from app.api.utils import timestamp_to_str_or_none
from app.models.lead import Lead
from app.repository.lead_repository import LeadRepository
from app.repository.posthog_event_repository import PostHogEventRepository
from app.schemas.lead_schema import LeadCreate, LeadResponse
from app.services.base_service import BaseService
from app.util.enums import EventName, OrderBy


class LeadService(BaseService[Lead]):
    def __init__(
        self, lead_repository: LeadRepository, event_repository: PostHogEventRepository
    ):
        self._event_repository = event_repository
        self.lead_repository = lead_repository
        super().__init__(lead_repository)

    async def get_or_create_lead(self, schema: LeadCreate):
        if schema.lead_id:
            return await self.get_by_id(schema.lead_id)
        else:
            new_lead = Lead()
            return await self.add(new_lead)

    async def get_by_id(self, lead_id: UUID) -> LeadResponse:
        lead = await super().get_by_id(lead_id)
        last_event = await self._event_repository.get_event(str(lead_id))

        if (
            last_event is None
            or last_event["timestamp"] == lead.last_processed_event_timestamp
        ):
            return lead
        else:
            lead_behaviors = await self._get_lead_behaviors(str(lead_id))
            lead = await self.patch(
                lead_id,
                behaviors=lead_behaviors,
                last_processed_event_timestamp=last_event["timestamp"],
            )
            return lead

    async def get_list(
        self, page: int, page_size: int
    ) -> tuple[list[LeadResponse], int]:
        leads, total = await self.lead_repository.read_list(page, page_size)
        for lead in leads:
            last_event = await self._event_repository.get_event(str(lead.id))

            if (
                last_event is None
                or last_event["timestamp"] == lead.last_processed_event_timestamp
            ):
                continue
            else:
                lead_behaviors = await self._get_lead_behaviors(str(lead.id))
                lead = await self.patch(
                    lead.id,
                    behaviors=lead_behaviors,
                    last_processed_event_timestamp=last_event["timestamp"],
                )
                leads[leads.index(lead)] = lead
        return leads, total

    async def _get_lead_behaviors(self, lead_id: str) -> dict:
        exported_file_event = await self._event_repository.get_event(
            lead_id, EventName.EXPORTED_FILE, OrderBy.ASC
        )
        signed_up_event = await self._event_repository.get_event(
            lead_id, EventName.SIGNED_UP, OrderBy.ASC
        )
        first_visit_event = await self._event_repository.get_event(
            lead_id, EventName.VISIT, OrderBy.ASC
        )
        last_visit_event = await self._event_repository.get_event(
            lead_id, EventName.VISIT, OrderBy.DESC
        )
        homepage_visits = await self._event_repository.count_by_event(
            lead_id, EventName.VISIT
        )
        viewed_pricing = await self._event_repository.count_by_event(
            lead_id, EventName.VIEWED_PRICING
        )

        exported_file_at = (
            exported_file_event["timestamp"] if exported_file_event else None
        )
        signed_up_at = signed_up_event["timestamp"] if signed_up_event else None
        first_visit_at = first_visit_event["timestamp"] if first_visit_event else None
        last_visit_at = last_visit_event["timestamp"] if last_visit_event else None

        behaviors_data = {
            "exported_file_at": timestamp_to_str_or_none(exported_file_at),
            "signed_up_at": timestamp_to_str_or_none(signed_up_at),
            "first_visit_at": timestamp_to_str_or_none(first_visit_at),
            "last_visit_at": timestamp_to_str_or_none(last_visit_at),
            "homepage_visits": homepage_visits,
            "viewed_pricing": viewed_pricing,
        }

        return behaviors_data
