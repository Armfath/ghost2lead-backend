"""Lead ORM model. Domain owns its table definition."""

from sqlalchemy import Column, DateTime, String

from app.models.base import BaseModel


class Lead(BaseModel):
    """Lead model - represents anonymous and signed-up visitors."""

    __tablename__ = "leads"

    ip_address_encrypted = Column(String(64), nullable=True)
    signed_up_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def has_registered(self) -> bool:
        return self.signed_up_at is not None
