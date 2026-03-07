from fastapi import APIRouter

from .v1 import v1_router


company_router = APIRouter(prefix="/api")


company_router.include_router(v1_router)
