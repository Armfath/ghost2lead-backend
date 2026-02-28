from sqlalchemy import text

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from scalar_fastapi import get_scalar_api_reference

from app.api.v1.router import routers as v1_routers
from app.core.config import configs
from app.core.database import db_session_maker
from app.core.exception_handlers import register_exception_handlers
from app.core.redis_client import ping_redis

app = FastAPI(
    title=configs.APP_NAME,
    openapi_url=f"{configs.API_PREFIX}/openapi.json",
    docs_url=None,
    redoc_url=None,
)

if configs.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=configs.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

register_exception_handlers(app)


@app.get("/health")
async def health_check():
    checks: dict[str, str] = {}

    try:
        async with db_session_maker() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "error"

    try:
        ok = await ping_redis()
        checks["redis"] = "ok" if ok else "error"
    except Exception:
        checks["redis"] = "error"

    all_ok = all(v == "ok" for v in checks.values())
    status_code = 200 if all_ok else 503
    return JSONResponse(
        {"status": "healthy" if all_ok else "degraded", "checks": checks},
        status_code=status_code,
    )


@app.get(f"{configs.API_PREFIX}/docs", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=configs.APP_NAME,
    )


app.include_router(v1_routers, prefix=configs.API_V1)
