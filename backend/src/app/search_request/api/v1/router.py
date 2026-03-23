from fastapi import APIRouter

from .endpoints import (
    search_request_endpoint,
)


v1_router = APIRouter(prefix="/v1/vacancies", tags=["Vacancies"])


v1_router.include_router(
    search_request_endpoint,
)
