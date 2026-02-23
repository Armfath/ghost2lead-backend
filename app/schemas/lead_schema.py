from uuid import UUID


from pydantic import BaseModel

from app.schemas.base_schema import ModelBaseInfo


class LeadCreate(BaseModel):
    lead_id: UUID | None = None


class LeadCreateResponse(ModelBaseInfo, BaseModel):
    pass


class LeadBehavior(BaseModel):
    homepage_visits: int
    viewed_pricing: int
    signed_up_at: str | None
    exported_file_at: str | None
    first_visit_at: str | None
    last_visit_at: str | None

class LeadResponse(ModelBaseInfo, BaseModel):
    behaviors: LeadBehavior | None = None
