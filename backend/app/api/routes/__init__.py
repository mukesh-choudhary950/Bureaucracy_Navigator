from fastapi import APIRouter
from app.api.routes import query, upload, auth, tasks, workflows

router = APIRouter()

router.include_router(query.router, prefix="/query", tags=["query"])
router.include_router(upload.router, prefix="/upload", tags=["upload"])
router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])
