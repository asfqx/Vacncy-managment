from typing import Sequence
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, status

from app.core import DBSession, RateLimitErrorResponse
from app.error_handler import error_schemas
from app.users.dependency import AuthenticatedActiveUser
from app.vacancy.filter import VacancyFilterDepends
from app.vacancy.models.vacancy import Vacancy
from app.vacancy.schemas.vacancy import VacancyCreateRequest, VacancyResponse
from app.vacancy.services.recomendation import RecomendationService
from app.vacancy.services.vacancy import VacancyService


router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=VacancyResponse,
    responses={
        400: {"model": error_schemas.BadRequestErrorResponse},
        401: {"model": error_schemas.UnauthorizedErrorResponse},
        409: {"model": error_schemas.AlreadyExistErrorResponse},
        429: {"model": RateLimitErrorResponse},
        500: {"model": error_schemas.InternalServerErrorResponse},
    },
)
async def create(
    data: VacancyCreateRequest,
    user: AuthenticatedActiveUser,
    sesssion: DBSession,
) -> Vacancy:
    return await VacancyService.create(user=user, data=data, session=sesssion)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=list[VacancyResponse],
    responses={
        401: {"model": error_schemas.UnauthorizedErrorResponse},
        404: {"model": error_schemas.NotFoundErrorResponse},
        429: {"model": RateLimitErrorResponse},
        500: {"model": error_schemas.InternalServerErrorResponse},
    },
)
async def get_all(
    user: AuthenticatedActiveUser,
    filters: VacancyFilterDepends,
    sesssion: DBSession,
) -> Sequence[Vacancy]:
    return await VacancyService.get_all(filters, session=sesssion)


@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    response_model=list[VacancyResponse],
    responses={
        401: {"model": error_schemas.UnauthorizedErrorResponse},
        404: {"model": error_schemas.NotFoundErrorResponse},
        429: {"model": RateLimitErrorResponse},
        500: {"model": error_schemas.InternalServerErrorResponse},
    },
)
async def search(
    user: AuthenticatedActiveUser,
    vacancy_title: str,
    filters: VacancyFilterDepends,
    background: BackgroundTasks,
    sesssion: DBSession,
) -> Sequence[Vacancy]:
    return await VacancyService.search(
        user_uuid=user.uuid,
        vacancy_name=vacancy_title,
        filters=filters,
        background=background,
        session=sesssion,
    )


@router.get(
    "/recommendation",
    status_code=status.HTTP_200_OK,
    response_model=list[VacancyResponse],
    responses={
        401: {"model": error_schemas.UnauthorizedErrorResponse},
        404: {"model": error_schemas.NotFoundErrorResponse},
        429: {"model": RateLimitErrorResponse},
        500: {"model": error_schemas.InternalServerErrorResponse},
    },
)
async def recomendation(
    user: AuthenticatedActiveUser,
    sesssion: DBSession,
    limit: int = 50,
    cursor: datetime | None = None,
) -> Sequence[Vacancy]:
    return await RecomendationService.recomendation(
        user_uuid=user.uuid,
        limit=limit,
        cursor=cursor,
        session=sesssion,
    )


@router.get(
    "/{vacancy_uuid}",
    status_code=status.HTTP_200_OK,
    response_model=VacancyResponse,
    responses={
        401: {"model": error_schemas.UnauthorizedErrorResponse},
        404: {"model": error_schemas.NotFoundErrorResponse},
        429: {"model": RateLimitErrorResponse},
        500: {"model": error_schemas.InternalServerErrorResponse},
    },
)
async def get(
    user: AuthenticatedActiveUser,
    vacancy_uuid: UUID,
    sesssion: DBSession,
) -> Vacancy:
    return await VacancyService.get(vacancy_uuid, session=sesssion)
