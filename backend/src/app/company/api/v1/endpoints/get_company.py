from uuid import UUID

from fastapi import APIRouter, status

from app.company.model import Company
from app.company.schema import CompanyCreateRequest, CompanyResponse, CompanyUpdateRequest
from app.company.service import CompanyService
from app.core import DBSession, RateLimitErrorResponse
from app.error_handler import error_schemas
from app.users.dependency import AuthenticatedActiveUser


router = APIRouter()


@router.get(
    "/me/",
    status_code=status.HTTP_200_OK,
    response_model=CompanyResponse,
    responses={
        401: {"model": error_schemas.UnauthorizedErrorResponse},
        404: {"model": error_schemas.NotFoundErrorResponse},
        429: {"model": RateLimitErrorResponse},
        500: {"model": error_schemas.InternalServerErrorResponse},
    },
)
async def get_mine(
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> Company:
    return await CompanyService.get_company(user, session=session)


@router.post(
    "/me/",
    status_code=status.HTTP_201_CREATED,
    response_model=CompanyResponse,
    responses={
        401: {"model": error_schemas.UnauthorizedErrorResponse},
        409: {"model": error_schemas.AlreadyExistErrorResponse},
        429: {"model": RateLimitErrorResponse},
        500: {"model": error_schemas.InternalServerErrorResponse},
    },
)
async def create_mine(
    data: CompanyCreateRequest,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> Company:
    return await CompanyService.create(user=user, data=data, session=session)


@router.patch(
    "/me/",
    status_code=status.HTTP_200_OK,
    response_model=CompanyResponse,
    responses={
        401: {"model": error_schemas.UnauthorizedErrorResponse},
        404: {"model": error_schemas.NotFoundErrorResponse},
        409: {"model": error_schemas.AlreadyExistErrorResponse},
        429: {"model": RateLimitErrorResponse},
        500: {"model": error_schemas.InternalServerErrorResponse},
    },
)
async def update_mine(
    data: CompanyUpdateRequest,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> Company:
    return await CompanyService.update(new_bio=data, current_user=user, session=session)


@router.get(
    "/{company_uuid}/",
    status_code=status.HTTP_200_OK,
    response_model=CompanyResponse,
    responses={
        401: {"model": error_schemas.UnauthorizedErrorResponse},
        404: {"model": error_schemas.NotFoundErrorResponse},
        429: {"model": RateLimitErrorResponse},
        500: {"model": error_schemas.InternalServerErrorResponse},
    },
)
async def get_by_id(
    company_uuid: UUID,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> Company:
    return await CompanyService.get_company_by_id(company_uuid, session=session)
