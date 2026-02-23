from uuid import UUID

from pydantic import BaseModel

from app.schemas.base_schema import ModelBaseInfo


class LeadCreate(BaseModel):
    lead_id: UUID | None = None


class LeadCreateResponse(ModelBaseInfo, BaseModel):
    pass
