from fastapi import APIRouter

from .endpoints import response_endpoint_router


v1_router = APIRouter(prefix="/v1/responses", tags=["Responses"])

v1_router.include_router(response_endpoint_router)
