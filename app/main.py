from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi import get_scalar_api_reference

from app.api.v1.router import routers as v1_routers
from app.core.config import configs
from app.core.exception_handlers import register_exception_handlers

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
    return {"status": "healthy"}


@app.get(f"{configs.API_PREFIX}/docs", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=configs.APP_NAME,
    )


app.include_router(v1_routers, prefix=configs.API_V1)
