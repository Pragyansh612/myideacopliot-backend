"""Custom exceptions"""


class AppException(Exception):
    """Base application exception"""
    def __init__(self, detail: str, status_code: int = 500):
        self.detail = detail
        self.status_code = status_code
        super().__init__(self.detail)


class AuthenticationError(AppException):
    """Authentication failed"""
    def __init__(self, detail: str = "Authentication required"):
        super().__init__(detail, 401)


class ForbiddenError(AppException):
    """Access forbidden"""
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(detail, 403)


class NotFoundError(AppException):
    """Resource not found"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail, 404)


class ConflictError(AppException):
    """Resource conflict"""
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(detail, 409)


class ValidationError(AppException):
    """Validation error"""
    def __init__(self, detail: str = "Validation error"):
        super().__init__(detail, 422)


class InternalServerError(AppException):
    """Internal server error"""
    def __init__(self, detail: str = "Internal server error"):
        super().__init__(detail, 500)