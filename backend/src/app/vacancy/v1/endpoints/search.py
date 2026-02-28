from typing import Sequence

from fastapi import APIRouter, status

from app.core import DBSession, RateLimitErrorResponse
from app.error_handler import error_schemas
from app.vacancy.filter import VacancyFilterDepends
from app.vacancy.model import Vacancy
from app.vacancy.schema import VacancyResponse
from app.vacancy.service import VacancyService
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
async def get_all(
    user: AuthenticatedActiveUser,
    sesssion: DBSession,
) -> Sequence[Vacancy]:

    return await VacancyService.get_all(session=sesssion)

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
    sesssion: DBSession,
) -> Sequence[Vacancy]:

    return await VacancyService.search(
        vacancy_name=vacancy_title,
        filters=filters,
        session=sesssion,
    )


