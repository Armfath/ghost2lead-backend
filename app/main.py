from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from config.settings import app_settings

app = FastAPI(
    title=app_settings.APP_NAME,
    docs_url=None,
    redoc_url=None, 
)


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/docs", include_in_schema=False)
def get_scalar_docs():
    return get_scalar_api_reference(
        openapi_url=app.openapi_url,
        title=app_settings.APP_NAME,
    )
