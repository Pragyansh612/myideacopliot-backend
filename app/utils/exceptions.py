"""Custom exceptions for the application"""
from fastapi import HTTPException, status


class AuthenticationError(HTTPException):
    """Authentication failed"""
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class AuthorizationError(HTTPException):
    """Authorization failed"""
    def __init__(self, detail: str = "Not authorized to access this resource"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class NotFoundError(HTTPException):
    """Resource not found"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ValidationError(HTTPException):
    """Validation failed"""
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ConflictError(HTTPException):
    """Resource conflict"""
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class InternalServerError(HTTPException):
    """Internal server error"""
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)