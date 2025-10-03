from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.middleware.auth import AuthMiddleware
from app.routers import auth, user, ideas, categories, phases, features

app = FastAPI(
    title="MyIdeaCopilot API",
    description="Backend API for MyIdeaCopilot - AI-powered idea management platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication middleware
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(categories.router)
app.include_router(ideas.router)
app.include_router(phases.router)
app.include_router(features.router)

@app.get("/")
async def root():
    return {
        "message": "MyIdeaCopilot",
        "status": "operational",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}