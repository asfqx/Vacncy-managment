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
    summary="Получить мою компанию",
    description=(
        "Возвращает компанию текущего авторизованного работодателя. "
        "Требуется JWT access-токен в заголовке Authorization."
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
            "description": "Компания не найдена",
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
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> Company:
    return await CompanyService.get_company(user, session=session)


@router.post(
    "/me/",
    status_code=status.HTTP_201_CREATED,
    summary="Создать мою компанию",
    description=(
        "Создает компанию для текущего авторизованного работодателя. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=CompanyResponse,
    responses={
        201: {
            "description": "Компания успешно создана",
            "model": CompanyResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        409: {
            "description": "Компания для пользователя уже существует",
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
async def create_mine(
    data: CompanyCreateRequest,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> Company:
    return await CompanyService.create(user=user, data=data, session=session)


@router.patch(
    "/me/",
    status_code=status.HTTP_200_OK,
    summary="Обновить мою компанию",
    description=(
        "Обновляет данные компании текущего авторизованного работодателя. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=CompanyResponse,
    responses={
        200: {
            "description": "Компания успешно обновлена",
            "model": CompanyResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Компания не найдена",
            "model": error_schemas.NotFoundErrorResponse,
        },
        409: {
            "description": "Конфликт при обновлении компании",
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
async def update_mine(
    data: CompanyUpdateRequest,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> Company:
    return await CompanyService.update(new_bio=data, current_user=user, session=session)


@router.get(
    "/by-user/{user_uuid}/",
    status_code=status.HTTP_200_OK,
    summary="Получить компанию пользователя",
    description="Возвращает компанию по UUID пользователя. Доступно администратору.",
    response_model=CompanyResponse,
)
async def get_by_user(
    user_uuid: UUID,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> Company:
    return await CompanyService.get_company_by_user(current_user=user, user_uuid=user_uuid, session=session)


@router.get(
    "/{company_uuid}/",
    status_code=status.HTTP_200_OK,
    summary="Получить компанию по UUID",
    description=(
        "Возвращает публичную информацию о компании по ее UUID. "
        "Требуется JWT access-токен в заголовке Authorization."
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
            "description": "Компания не найдена",
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
async def get_by_id(
    company_uuid: UUID,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> Company:
    return await CompanyService.get_company_by_id(company_uuid, session=session)
