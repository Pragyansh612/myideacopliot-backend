"""Main FastAPI application"""
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.middleware.auth import AuthMiddleware
from app.routers import auth, user
from app.schemas.response import ErrorResponse


# Create FastAPI app
app = FastAPI(
    title="MyIdeaCopilot API",
    description="Backend API for MyIdeaCopilot - Phase 1: User Management & Settings",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Add authentication middleware
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(user.router)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "MyIdeaCopilot API is running",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Welcome to MyIdeaCopilot API",
        "version": "1.0.0",
        "phase": "Phase 1: User Management & Settings",
        "docs": "/docs",
        "health": "/health"
    }


# Global exception handlers

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            message="Validation error",
            error_code="VALIDATION_ERROR",
            details={"errors": exc.errors()}
        ).dict()
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            message=str(exc.detail),
            error_code=f"HTTP_{exc.status_code}"
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    # Log the error in production
    if settings.DEBUG:
        import traceback
        traceback.print_exc()
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            message="Internal server error" if not settings.DEBUG else str(exc),
            error_code="INTERNAL_SERVER_ERROR"
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )