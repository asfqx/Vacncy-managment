from uuid import UUID

from fastapi import APIRouter, status

from app.core import DBSession, RateLimitErrorResponse
from app.error_handler import error_schemas
from app.users.dependency import AuthenticatedActiveUser
from app.company.schema import CompanyResponse
from app.company.model import Company
from app.company.service import CompanyService


router = APIRouter()

@router.get(
    "/{company_uuid}",
    status_code=status.HTTP_200_OK,
    summary="Вывести компанию по uuid",
    description=(
        "Возвращает информацию о компании по uuid"
        "Требуется JWT access-токен в заголовке Authorization и роль Администратор. "
        "Если токен отсутствует или недействителен — возвращается ошибка 401."
    ),
    response_model=CompanyResponse,
    responses={
        200: {
            "description": "Компания успешно получена",
            "model": CompanyResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Поисковые запросы не найдены",
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
    company_uuid: UUID,
    user: AuthenticatedActiveUser,
    sesssion: DBSession,
) -> Company:

    return await CompanyService.get_company_by_id(company_uuid, session=sesssion)


@router.get(
    "/{company_uuid}",
    status_code=status.HTTP_200_OK,
    summary="Вывести компанию по uuid",
    description=(
        "Возвращает информацию о компании по uuid"
        "Требуется JWT access-токен в заголовке Authorization и роль Администратор. "
        "Если токен отсутствует или недействителен — возвращается ошибка 401."
    ),
    response_model=CompanyResponse,
    responses={
        200: {
            "description": "Компания успешно получена",
            "model": CompanyResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Поисковые запросы не найдены",
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
async def get_mine(
    company_uuid: UUID,
    user: AuthenticatedActiveUser,
    sesssion: DBSession,
) -> Company:

    return await CompanyService.get_company(user, session=sesssion)
