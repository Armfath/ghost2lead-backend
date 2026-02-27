from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB

from app.models.base import BaseModel


class Lead(BaseModel):
    __tablename__ = "leads"

    last_processed_event_timestamp = Column(DateTime(timezone=True), nullable=True)
    behaviors = Column(JSONB, nullable=True)
    profile = Column(JSONB, nullable=True)
    actions = Column(JSONB, nullable=True)
    enriched_at = Column(DateTime(timezone=True), nullable=True)
