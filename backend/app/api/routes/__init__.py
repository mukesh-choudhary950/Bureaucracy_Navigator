from fastapi import APIRouter
from app.api.routes import query, upload

router = APIRouter()

router.include_router(query.router, prefix="/query", tags=["query"])
router.include_router(upload.router, prefix="/upload", tags=["upload"])
