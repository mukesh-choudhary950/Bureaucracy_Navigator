from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.routes import router as api_router
from app.core.config import settings
from app.core.logging import setup_logging
from app.services.initialization import initialization_service


# Initialize logging
setup_logging()

app = FastAPI(
    title="Bureaucracy Navigator Agent",
    description="AI agent for government procedures",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize system on startup"""
    await initialization_service.initialize_system()


# Root endpoint
@app.get("/")
async def root():
    return {"message": "Bureaucracy Navigator Agent API"}


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# Initialization status
@app.get("/init-status")
async def get_init_status():
    return initialization_service.get_initialization_status()


# Run server directly
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )