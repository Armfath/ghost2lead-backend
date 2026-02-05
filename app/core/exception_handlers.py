from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.exceptions import APIException, ErrorCode
from app.helpers.sanitize_header_value import sanitize_header_value
from app.schemas.base import APIError
from config.settings import app_settings


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(APIException)
    async def api_exception_handler(_, exc: APIException):
        return JSONResponse(
            status_code=exc.status_code,
            content=APIError(error=exc.error_code, message=exc.message).model_dump(
                mode="json"
            ),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=APIError(
                error=ErrorCode.VALIDATION_ERROR, message=exc.errors()
            ).model_dump(mode="json"),
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(_, exc: Exception):
        error_message = f"{exc.__class__.__name__}: {exc}"
        headers = {}
        if app_settings.DEBUG:
            headers["X-Server-Error"] = sanitize_header_value(error_message)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers=headers,
            content=APIError(
                error=ErrorCode.INTERNAL_SERVER_ERROR,
                message="Something went wrong",
            ).model_dump(mode="json"),
        )
