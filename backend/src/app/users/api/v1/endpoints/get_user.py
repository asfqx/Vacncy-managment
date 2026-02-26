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
    summary="Получить профиль текущего пользователя",
    description=(
        "Возвращает информацию о текущем аутентифицированном пользователе. "
        "Требуется JWT access-токен в заголовке Authorization. "
        "Если токен отсутствует или недействителен — возвращается ошибка 401."
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
    sesssion: DBSession,
) -> User:

    return await UserService.get_user_profile(
        current_user=user,
        session=sesssion,
    )


@router.patch(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Обновить email и/или имя пользователя",
    description=(
        "Позволяет частично обновить профиль текущего пользователя: имя пользователя (username) и/или email. "  # noqa: E501
        "Email должен быть уникальным. Возвращает обновлённый профиль. "
        "Требуется авторизация через JWT access-токен в заголовке Authorization.\n\n"
        "Необязательные параметры: \n"
        "- **username** — новое имя пользователя.\n"
        "- **email** — новый email.\n"
        "- **avatar_url** — ссылка на аватар.\n\n"
    ),
    response_model=UpdateUserProfileResponse,
    responses={
        200: {
            "description": "Профиль пользователя успешно обновлён",
            "model": UpdateUserProfileRequest,
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
            "description": "Email уже используется другим пользователем",
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
    summary="Получить pre-signed URL для загрузки аватара",
    response_model=CreatePreSignedURLResponse,
    description=(
        "Генерирует временную ссылку (pre-signed URL) для загрузки аватара в "
        "S3-совместимое хранилище. Срок действия ссылки — 15 минут. "
        "Путь формируется автоматически, пример: `avatars/{user_uuid}/{uuid}.png`.\n\n"
        "⚠️ Необходимо вызвать этот эндпоинт **перед** фактической загрузкой файла "
        "через Patch-запрос к полученному URL."
    ),
    responses={
        200: {
            "description": "Успешно получена ссылка",
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
    },
)
async def upload_avatar(
    user: AuthenticatedActiveUser,
) -> dict[str, str]:

    return await UserService.upload_avatar(user=user)
