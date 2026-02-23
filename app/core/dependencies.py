from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import configs
from app.core.database import get_db_transaction
from app.repository.lead_repository import LeadRepository
from app.schemas.base_schema import FindBase
from app.services.lead_service import LeadService

# Dependency for getting database transactions.
DBTransactionDep = Annotated[AsyncSession, Depends(get_db_transaction)]


# Lead dependencies
def get_lead_repository(session: DBTransactionDep) -> LeadRepository:
    return LeadRepository(session)


def get_lead_service(
    repo: Annotated[LeadRepository, Depends(get_lead_repository)],
) -> LeadService:
    return LeadService(repo)


LeadRepositoryDep = Annotated[LeadRepository, Depends(get_lead_repository)]
LeadServiceDep = Annotated[LeadService, Depends(get_lead_service)]

# Pagination dependencies
def get_pagination_params(
    page: int = Query(configs.PAGE, ge=1),
    page_size: int = Query(
        configs.PAGE_SIZE,
        ge=configs.PAGE_SIZE_MIN,
        le=configs.PAGE_SIZE_MAX,
    ),
) -> FindBase:
    return FindBase(page=page, page_size=page_size)

PaginationParamsDep = Annotated[FindBase, Depends(get_pagination_params)]
