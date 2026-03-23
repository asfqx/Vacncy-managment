from fastapi import APIRouter

from .v1 import v1_router


response_router = APIRouter(prefix="/api")

response_router.include_router(v1_router)
