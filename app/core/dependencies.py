from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_transaction
from app.repository.lead_repository import LeadRepository
from app.services.lead_service import LeadService

# Dependency for getting database transactions.
DBTransactionDep = Annotated[AsyncSession, Depends(get_db_transaction)]

# Dependency for getting client IP.
def get_client_ip(request: Request) -> str | None:
    """Extract client IP from request headers."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return None


ClientIPDep = Annotated[str | None, Depends(get_client_ip)]


# Lead dependencies
def get_lead_repository(session: DBTransactionDep) -> LeadRepository:
    return LeadRepository(session)


def get_lead_service(
    repo: Annotated[LeadRepository, Depends(get_lead_repository)],
) -> LeadService:
    return LeadService(repo)


LeadRepositoryDep = Annotated[LeadRepository, Depends(get_lead_repository)]
LeadServiceDep = Annotated[LeadService, Depends(get_lead_service)]
