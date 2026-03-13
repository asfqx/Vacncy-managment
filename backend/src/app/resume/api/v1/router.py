from fastapi import APIRouter

from .endpoints import search_enpoint_router


v1_router = APIRouter(prefix="/v1/resumes", tags=["Resumes"])

v1_router.include_router(search_enpoint_router)