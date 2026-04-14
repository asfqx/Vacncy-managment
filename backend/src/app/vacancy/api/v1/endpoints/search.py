from typing import Sequence
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, status

from app.core import DBSession, RateLimitErrorResponse
from app.error_handler import error_schemas
from app.users.dependency import AuthenticatedActiveUser
from app.vacancy.filter import VacancyFilterDepends
from app.vacancy.model import Vacancy
from app.vacancy.schema import VacancyCreateRequest, VacancyResponse
from app.vacancy.services.recomendation import RecomendationService
from app.vacancy.services.vacancy import VacancyService


router = APIRouter()


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Создать вакансию",
    description=(
        "Создает новую вакансию от имени авторизованного работодателя. "
        "Требуется JWT access-токен в заголовке Authorization. "
        "Если пользователь не авторизован, не имеет доступа или передал некорректные данные, "
        "возвращается соответствующая ошибка."
    ),
    response_model=VacancyResponse,
    responses={
        201: {
            "description": "Вакансия успешно создана",
            "model": VacancyResponse,
        },
        400: {
            "description": "Переданы некорректные данные вакансии",
            "model": error_schemas.BadRequestErrorResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        409: {
            "description": "Конфликт при создании вакансии",
            "model": error_schemas.AlreadyExistErrorResponse,
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
async def create(
    data: VacancyCreateRequest,
    user: AuthenticatedActiveUser,
    sesssion: DBSession,
) -> Vacancy:
    
    return await VacancyService.create(user=user, data=data, session=sesssion)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Получить список вакансий",
    description=(
        "Возвращает список вакансий с учетом фильтров и курсорной пагинации. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=list[VacancyResponse],
    responses={
        200: {
            "description": "Список вакансий успешно получен",
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
        "Выполняет поиск вакансий по строке запроса с учетом фильтров. "
        "Поисковый запрос пользователя сохраняется для дальнейших рекомендаций. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=list[VacancyResponse],
    responses={
        200: {
            "description": "Результаты поиска вакансий успешно получены",
            "model": list[VacancyResponse],
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Подходящие вакансии не найдены",
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
    summary="Получить рекомендации по вакансиям",
    description=(
        "Возвращает список рекомендованных вакансий на основе истории поисковых запросов пользователя. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=list[VacancyResponse],
    responses={
        200: {
            "description": "Рекомендации по вакансиям успешно получены",
            "model": list[VacancyResponse],
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Рекомендации не найдены",
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
    cursor_uuid: UUID | None = None,
) -> Sequence[Vacancy]:
    
    return await RecomendationService.recomendation(
        user_uuid=user.uuid,
        limit=limit,
        cursor=cursor,
        cursor_uuid=cursor_uuid,
        session=sesssion,
    )


@router.get(
    "/{vacancy_uuid}",
    status_code=status.HTTP_200_OK,
    summary="Получить вакансию по UUID",
    description=(
        "Возвращает полную информацию о вакансии по ее UUID. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=VacancyResponse,
    responses={
        200: {
            "description": "Вакансия успешно получена",
            "model": VacancyResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Вакансия не найдена",
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


@router.delete(
    "/{vacancy_uuid}",
    status_code=status.HTTP_200_OK,
    summary="Удалить вакансию",
    description=(
        "Удаляет или архивирует вакансию по UUID в зависимости от бизнес-логики сервиса. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=VacancyResponse,
    responses={
        200: {
            "description": "Вакансия успешно удалена",
            "model": VacancyResponse,
        },
        400: {
            "description": "Вакансию нельзя удалить в текущем состоянии",
            "model": error_schemas.BadRequestErrorResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Вакансия не найдена",
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
async def delete(
    user: AuthenticatedActiveUser,
    vacancy_uuid: UUID,
    sesssion: DBSession,
) -> Vacancy:
    return await VacancyService.delete(
        user_uuid=user.uuid,
        vacancy_uuid=vacancy_uuid,
        session=sesssion,
    )
