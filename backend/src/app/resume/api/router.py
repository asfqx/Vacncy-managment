from fastapi import APIRouter

from .v1 import v1_router


resume_router = APIRouter(prefix="/api")

resume_router.include_router(v1_router)