"""Common response schemas"""
from typing import Any, Dict, Optional
from pydantic import BaseModel


class BaseResponse(BaseModel):
    """Base response model"""
    success: bool = True
    message: str = "Success"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class SuccessResponse(BaseResponse):
    """Success response model"""
    pass