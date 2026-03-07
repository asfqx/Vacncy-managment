from fastapi import APIRouter

from .endpoints import (
    company_router,
)


v1_router = APIRouter(prefix="/v1/companies", tags=["Companies"])


v1_router.include_router(
    company_router,
)

