from typing import Any

from fastapi import APIRouter, status

from app.core import DBSession, RateLimitErrorResponse
from app.error_handler import error_schemas
from app.users.dependency import AuthenticatedActiveUser
from app.users.model import User
from app.users.schema import (
    CreatePreSignedURLResponse,
    GetUserProfileResponse,
    UpdateUserProfileRequest,
    UpdateUserProfileResponse,
)
from app.users.service import UserService


router = APIRouter(prefix="/me")


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Получить мой профиль",
    description=(
        "Возвращает профиль текущего авторизованного пользователя. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=GetUserProfileResponse,
    responses={
        200: {
            "description": "Профиль пользователя успешно получен",
            "model": GetUserProfileResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Пользователь не найден",
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
async def get_user_profile(
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> User:
    return await UserService.get_user_profile(
        current_user=user,
        session=session,
    )


@router.patch(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Обновить мой профиль",
    description=(
        "Обновляет email, username, ФИО или avatar_url текущего пользователя. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=UpdateUserProfileResponse,
    responses={
        200: {
            "description": "Профиль пользователя успешно обновлен",
            "model": UpdateUserProfileResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Пользователь не найден",
            "model": error_schemas.NotFoundErrorResponse,
        },
        409: {
            "description": "Email или username уже заняты",
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
async def update_bio(
    new_bio: UpdateUserProfileRequest,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> dict[str, Any]:
    return await UserService.update_bio(
        new_bio=new_bio,
        current_user=user,
        session=session,
    )


@router.get(
    "/avatar/upload-url",
    status_code=status.HTTP_200_OK,
    summary="Получить ссылку для загрузки аватара",
    description=(
        "Возвращает pre-signed URL для загрузки аватара пользователя в S3-совместимое хранилище. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=CreatePreSignedURLResponse,
    responses={
        200: {
            "description": "Ссылка для загрузки аватара успешно получена",
            "model": CreatePreSignedURLResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
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
async def upload_avatar(
    user: AuthenticatedActiveUser,
) -> dict[str, str]:
    return await UserService.upload_avatar(user=user)
