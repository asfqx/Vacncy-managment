from typing import Sequence
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, status, BackgroundTasks

from app.core import DBSession, RateLimitErrorResponse
from app.error_handler import error_schemas
from app.vacancy.filter import VacancyFilterDepends
from app.vacancy.models.vacancy import Vacancy
from app.vacancy.schemas.vacancy import VacancyResponse
from app.vacancy.services.vacancy import VacancyService
from app.vacancy.services.recomendation import RecomendationService
from app.users.dependency import AuthenticatedActiveUser


router = APIRouter()

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Вывести все вакансии",
    description=(
        "Возвращает информацию обо всех вакансиях. "
        "Требуется JWT access-токен в заголовке Authorization. "
        "Если токен отсутствует или недействителен — возвращается ошибка 401."
    ),
    response_model=list[VacancyResponse],
    responses={
        200: {
            "description": "Вакансии успешно получены",
            "model": list[VacancyResponse],
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Вакансии не найдены",
            "model": error_schemas.NotFoundErrorResponse,
        },
        429: {
            "description": "Превышен лимит запросов",
            "model": RateLimitErrorResponse,
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "model": error_schemas.InternalServerErrorResponse,
        },
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
    summary="Поиск вакансий",
    description=(
        "Возвращает информацию о найденных вакансиях. "
        "Требуется JWT access-токен в заголовке Authorization. "
        "Если токен отсутствует или недействителен — возвращается ошибка 401."
    ),
    response_model=list[VacancyResponse],
    responses={
        200: {
            "description": "Вакансии успешно получены",
            "model": VacancyResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Вакансии не найдены",
            "model": error_schemas.NotFoundErrorResponse,
        },
        429: {
            "description": "Превышен лимит запросов",
            "model": RateLimitErrorResponse,
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "model": error_schemas.InternalServerErrorResponse,
        },
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
    summary="Рекомендации вакансий",
    description=(
        "Возвращает информацию о найденных рекомендованных вакансиях. "
        "Требуется JWT access-токен в заголовке Authorization. "
        "Если токен отсутствует или недействителен — возвращается ошибка 401."
    ),
    response_model=list[VacancyResponse],
    responses={
        200: {
            "description": "Вакансии успешно получены",
            "model": VacancyResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Вакансии не найдены",
            "model": error_schemas.NotFoundErrorResponse,
        },
        429: {
            "description": "Превышен лимит запросов",
            "model": RateLimitErrorResponse,
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "model": error_schemas.InternalServerErrorResponse,
        },
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
    summary="Вывести вакансию",
    description=(
        "Возвращает информацию о вакансии. "
        "Требуется JWT access-токен в заголовке Authorization. "
        "Если токен отсутствует или недействителен — возвращается ошибка 401."
    ),
    response_model=VacancyResponse,
    responses={
        200: {
            "description": "Вакансии успешно получены",
            "model": VacancyResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Вакансии не найдены",
            "model": error_schemas.NotFoundErrorResponse,
        },
        429: {
            "description": "Превышен лимит запросов",
            "model": RateLimitErrorResponse,
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "model": error_schemas.InternalServerErrorResponse,
        },
    },
)
async def get(
    user: AuthenticatedActiveUser,
    vacancy_uuid: UUID,
    sesssion: DBSession,
) -> Vacancy:

    return await VacancyService.get(vacancy_uuid, session=sesssion)