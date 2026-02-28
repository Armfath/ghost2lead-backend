from datetime import datetime
from uuid import UUID

from app.api.utils import timestamp_to_str_or_none
from app.core.exceptions import ForbiddenError
from app.models.lead import Lead
from app.models.user import User
from app.repository.lead_repository import LeadRepository
from app.repository.posthog_event_repository import PostHogEventRepository
from app.schemas.lead_schema import LeadBehavior, LeadCreate, LeadResponse
from app.services.agent_service import AgentService
from app.services.base_service import BaseService
from app.util.enums import EventName, OrderBy, UserType


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

    async def get_lead(self, lead_id: UUID, user: User) -> Lead:
        lead = await self.get_by_id(lead_id)
        if user.user_type == UserType.CUSTOMER and user.lead_id != lead_id:
            raise ForbiddenError("Access denied to this lead")
        return lead

    async def _get_lead_behaviors_with_last_event(
        self, lead_id: str
    ) -> tuple[dict | None, LeadBehavior | None]:

        last_event = await self._event_repository.get_event(lead_id)

        if last_event is None:
            return None, None

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

        return last_event, behaviors_data

    async def enrich_lead(self, lead_id: UUID) -> LeadResponse:
        lead = await self.get_by_id(lead_id)

        if lead.behaviors is None:
            last_event, lead_behaviors = await self._get_lead_behaviors_with_last_event(
                str(lead_id)
            )
            if last_event is None:
                lead = await self.patch(lead_id, enriched_at=datetime.now())
            else:
                profile, actions = AgentService().run_agent(lead_behaviors)
                lead = await self.patch(
                    lead_id,
                    behaviors=lead_behaviors,
                    last_processed_event_timestamp=last_event.get("timestamp"),
                    profile=profile.model_dump() if profile else None,
                    actions=[a.model_dump() for a in actions] if actions else None,
                    enriched_at=datetime.now(),
                )
        else:
            last_event = await self._event_repository.get_event(str(lead_id))

            if (
                last_event is None
                or last_event.get("timestamp") == lead.last_processed_event_timestamp
            ):
                lead = await self.patch(
                    lead_id,
                    enriched_at=datetime.now(),
                )
            else:
                last_event, lead_behaviors = await self._get_lead_behaviors_with_last_event(
                    str(lead_id)
                )
                if last_event is None:
                    lead = await self.patch(lead_id, enriched_at=datetime.now())
                else:
                    profile, actions = AgentService().run_agent(lead_behaviors)
                    lead = await self.patch(
                        lead_id,
                        behaviors=lead_behaviors,
                        last_processed_event_timestamp=last_event.get("timestamp"),
                        profile=profile.model_dump() if profile else None,
                        actions=[a.model_dump() for a in actions] if actions else None,
                        enriched_at=datetime.now(),
                    )
        return lead
