from enum import Enum

from fastapi import status


class ErrorCode(Enum):
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    BAD_REQUEST = "BAD_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    FORBIDDEN = "FORBIDDEN"


class APIException(Exception):
    """Base class for all API exceptions"""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR
    message: str = "Internal Server Error"


class NotFoundError(APIException):
    status_code = status.HTTP_404_NOT_FOUND

    def __init__(self, entity: str, identifier: int):
        self.error_code = ErrorCode.NOT_FOUND
        self.message = f"{entity} with ID {identifier} not found"


class UnauthorizedError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = ErrorCode.UNAUTHORIZED
    message = "User is not authorized to access this resource"


class BadRequestError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    error_code = ErrorCode.BAD_REQUEST
    message = "Invalid request"

    def __init__(self, message: str):
        self.message = message


class ValidationError(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = ErrorCode.VALIDATION_ERROR
    message = "Errors occurred while validating the request"

    def __init__(self, messages: list[str]):
        self.message = messages

class ForbiddenError(APIException):
    status_code = status.HTTP_403_FORBIDDEN
    error_code = ErrorCode.FORBIDDEN
    message = "Access is forbidden"
