from fastapi import APIRouter

from app.api.v1.routers.auth import router as auth_router
from app.api.v1.routers.lead import router as lead_router

routers = APIRouter()

router_list = [
    auth_router,
    lead_router,
]

for router in router_list:
    routers.include_router(router)
