from typing import Any

from fastapi import APIRouter, Response, status

from app.auth.schemas import (
    CreateTokenPairResponse,
    GetAccessTokenRequest,
    GetTokenPairResponse,
    GetUserRoleResponse,
)
from app.auth.services import AuthService
from app.core import DBSession, RateLimitErrorResponse
from app.error_handler import error_schemas
from app.users.dependency import AuthenticatedUser


router = APIRouter()


@router.post(
    "/refresh",
    status_code=status.HTTP_200_OK,
    summary="Обновление JWT токена",
    response_model=GetTokenPairResponse,
    description=(
        "Обновляет пару access/refresh токенов по существующему `refresh_token`,"
        "переданному в cookie. Если токен невалиден или отсутствует "
        "— возвращает ошибку."
        "Также применяется ограничение частоты запросов — не более 2 в минуту."
    ),
    responses={
        200: {
            "description": "Токен успешно обновлён",
            "model": GetTokenPairResponse,
        },
        400: {
            "description": "Некорректный запрос",
            "model": error_schemas.BadRequestErrorResponse,
        },
        429: {
            "description": "Пользователь превысил число запросов",
            "model": RateLimitErrorResponse,
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "model": error_schemas.InternalServerErrorResponse,
        },
    },
)
async def refresh_token(
    refresh_data: CreateTokenPairResponse,
    user: AuthenticatedUser,
    response: Response,
    session: DBSession,
) -> dict[str, Any]:

    return await AuthService.refresh_token(
        refresh_data.refresh_token,
        user,
        response,
        session
    )


@router.post(
    "/check_role",
    status_code=status.HTTP_200_OK,
    summary="Проверка валидности JWT токена",
    response_model=GetUserRoleResponse,
    description=(
        "Проверяет валидность access токена и возвращает информацию о пользователе. "
        "Если токен валиден — возвращает данные пользователя (UUID, роль и т.д.). "
        "Если токен невалиден или истёк — возвращает ошибку 400.\n\n"
        "Параметры:\n"
        "- **access_token** — JWT access токен для проверки.\n\n"
        "Возвращает:\n"
        "- **role** — роль пользователя в системе.\n\n"
    ),
    responses={
        200: {
            "description": "JWT токен валиден, возвращена информация о пользователе",
            "model": GetUserRoleResponse,
        },
        400: {
            "description": "JWT токен невалиден или истёк",
            "model": error_schemas.BadRequestErrorResponse,
        },
        429: {
            "description": "Превышение лимита запросов",
            "model": RateLimitErrorResponse,
        },
        500: {
            "description": "Внутренняя ошибка сервера",
            "model": error_schemas.InternalServerErrorResponse,
        },
    },
)
async def check_role(
    access_data: GetAccessTokenRequest,
    session: DBSession,
) -> dict[str, Any]:

    return await AuthService.get_role_from_jwt(access_data.access_token, session)

