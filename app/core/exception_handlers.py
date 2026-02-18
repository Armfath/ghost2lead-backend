from fastapi import FastAPI, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import configs
from app.core.exceptions import APIException, ErrorCode
from app.schemas.base_schema import APIError
from app.util.normalize_text import normalize_text


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
        if configs.DEBUG:
            headers["X-Server-Error"] = normalize_text(error_message)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            headers=headers,
            content=APIError(
                error=ErrorCode.INTERNAL_SERVER_ERROR,
                message="Something went wrong",
            ).model_dump(mode="json"),
        )
