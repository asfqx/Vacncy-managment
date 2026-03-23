from fastapi import APIRouter

from .v1 import v1_router


search_router = APIRouter(prefix="/api")


search_router.include_router(v1_router)
