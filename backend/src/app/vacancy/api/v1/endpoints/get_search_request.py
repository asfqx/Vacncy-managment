from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, status

from app.core import DBSession, RateLimitErrorResponse
from app.error_handler import error_schemas
from app.users.dependency import AuthenticatedActiveUser
from app.vacancy.schemas.search_request import SearchRequestResponse
from app.vacancy.models.search_request import SearchRequest
from app.vacancy.services.search_request import SearchRequestService


router = APIRouter(prefix="/search-requests")

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Вывести все поисковые запросы пользователя",
    description=(
        "Возвращает информацию обо всех поисковых запросах "
        "Требуется JWT access-токен в заголовке Authorization и роль Администратор. "
        "Если токен отсутствует или недействителен — возвращается ошибка 401."
    ),
    response_model=list[SearchRequestResponse],
    responses={
        200: {
            "description": "Поисковые запросы успешно получены",
            "model": list[SearchRequestResponse],
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
async def get_all(
    user_uuid: UUID,
    user: AuthenticatedActiveUser,
    sesssion: DBSession,
) -> Sequence[SearchRequest]:

    return await SearchRequestService.get_all(user_uuid, user, session=sesssion)
