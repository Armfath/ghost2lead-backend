from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field

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


class ConfidenceLevel(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class ProfilingOutput(BaseModel):
    persona: str = Field(..., description="The persona of the lead")
    primary_objection: str = Field(..., description="The primary objection of the lead")
    strongest_signal: str = Field(..., description="The strongest signal of the lead")
    confidence: ConfidenceLevel = Field(
        ..., description="The confidence level of the lead"
    )


class ActionOutput(BaseModel):
    actions: list["Action"] = Field(..., description="The actions to take")


class Action(BaseModel):
    action: str = Field(..., description="The action to take")
    reasoning: str = Field(..., description="The reasoning for the action")


class LeadResponse(ModelBaseInfo, BaseModel):
    behaviors: LeadBehavior | None = None
    profile: ProfilingOutput | None = None
    actions: list[Action] | None = None
    enriched_at: datetime | None = None
