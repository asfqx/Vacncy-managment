from typing import Sequence
from uuid import UUID

from fastapi import APIRouter, status

from app.core import DBSession, RateLimitErrorResponse
from app.error_handler import error_schemas
from app.response.model import Response
from app.response.schema import (
    AIResponseCreateRequest,
    AIResponseCreateResponse,
    ResponseCreateRequest,
    ResponseResponse,
    ResponseUpdateStatusRequest,
)
from app.response.service import ResponseService
from app.users.dependency import AuthenticatedActiveUser


router = APIRouter()


@router.post(
    "/generate",
    status_code=status.HTTP_200_OK,
    summary="Сгенерировать письмо-отклик на вакансию с помощью AI",
    description=(
        "Генерирует письмо-отклик на основе описания резюме, опыта работы кандидата "
        "и описания вакансии. Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=AIResponseCreateResponse,
    responses={
        200: {"description": "Письмо-отклик успешно сгенерировано", "model": AIResponseCreateResponse},
        400: {"description": "Переданы некорректные данные для генерации письма", "model": error_schemas.BadRequestErrorResponse},
        401: {"description": "Пользователь не авторизован", "model": error_schemas.UnauthorizedErrorResponse},
        403: {"description": "Недостаточно прав для генерации письма", "model": error_schemas.ForbiddenErrorResponse},
        404: {"description": "Резюме или вакансия не найдены", "model": error_schemas.NotFoundErrorResponse},
        429: {"description": "Превышен лимит запросов", "model": RateLimitErrorResponse},
        500: {"description": "Внутренняя ошибка сервера", "model": error_schemas.InternalServerErrorResponse},
    },
)
async def generate_response(
    data: AIResponseCreateRequest,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> AIResponseCreateResponse:
    return await ResponseService.generate(user=user, data=data, session=session)


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    summary="Создать отклик",
    description="Создает отклик на вакансию и сохраняет письмо кандидата.",
    response_model=ResponseResponse,
    responses={
        201: {"description": "Отклик успешно создан", "model": ResponseResponse},
        400: {"description": "Переданы некорректные данные отклика", "model": error_schemas.BadRequestErrorResponse},
        401: {"description": "Пользователь не авторизован", "model": error_schemas.UnauthorizedErrorResponse},
        403: {"description": "Недостаточно прав для создания отклика", "model": error_schemas.ForbiddenErrorResponse},
        404: {"description": "Резюме или вакансия не найдены", "model": error_schemas.NotFoundErrorResponse},
        409: {"description": "Отклик уже существует", "model": error_schemas.AlreadyExistErrorResponse},
        429: {"description": "Превышен лимит запросов", "model": RateLimitErrorResponse},
        500: {"description": "Внутренняя ошибка сервера", "model": error_schemas.InternalServerErrorResponse},
    },
)
async def create_response_item(
    data: ResponseCreateRequest,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> Response:
    return await ResponseService.create(user=user, data=data, session=session)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Получить список откликов",
    description="Возвращает список откликов для текущего пользователя в зависимости от его роли.",
    response_model=list[ResponseResponse],
    responses={
        200: {"description": "Отклики успешно получены", "model": list[ResponseResponse]},
        401: {"description": "Пользователь не авторизован", "model": error_schemas.UnauthorizedErrorResponse},
        403: {"description": "Недостаточно прав для просмотра откликов", "model": error_schemas.ForbiddenErrorResponse},
        404: {"description": "Отклики не найдены", "model": error_schemas.NotFoundErrorResponse},
        429: {"description": "Превышен лимит запросов", "model": RateLimitErrorResponse},
        500: {"description": "Внутренняя ошибка сервера", "model": error_schemas.InternalServerErrorResponse},
    },
)
async def get_all_responses(
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> Sequence[Response]:
    return await ResponseService.get_all(user=user, session=session)


@router.get(
    "/{response_uuid}",
    status_code=status.HTTP_200_OK,
    summary="Получить отклик по UUID",
    description="Возвращает один отклик, если у пользователя есть права на его просмотр.",
    response_model=ResponseResponse,
    responses={
        200: {"description": "Отклик успешно получен", "model": ResponseResponse},
        401: {"description": "Пользователь не авторизован", "model": error_schemas.UnauthorizedErrorResponse},
        403: {"description": "Недостаточно прав для просмотра отклика", "model": error_schemas.ForbiddenErrorResponse},
        404: {"description": "Отклик не найден", "model": error_schemas.NotFoundErrorResponse},
        429: {"description": "Превышен лимит запросов", "model": RateLimitErrorResponse},
        500: {"description": "Внутренняя ошибка сервера", "model": error_schemas.InternalServerErrorResponse},
    },
)
async def get_response(
    response_uuid: UUID,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> Response:
    return await ResponseService.get(user=user, response_uuid=response_uuid, session=session)


@router.patch(
    "/{response_uuid}/status",
    status_code=status.HTTP_200_OK,
    summary="Изменить статус отклика",
    description="Работодатель или администратор может изменить статус отклика на ACCEPTED или REJECTED.",
    response_model=ResponseResponse,
    responses={
        200: {"description": "Статус отклика успешно обновлен", "model": ResponseResponse},
        400: {"description": "Переданы некорректные данные", "model": error_schemas.BadRequestErrorResponse},
        401: {"description": "Пользователь не авторизован", "model": error_schemas.UnauthorizedErrorResponse},
        403: {"description": "Недостаточно прав для изменения статуса", "model": error_schemas.ForbiddenErrorResponse},
        404: {"description": "Отклик не найден", "model": error_schemas.NotFoundErrorResponse},
        429: {"description": "Превышен лимит запросов", "model": RateLimitErrorResponse},
        500: {"description": "Внутренняя ошибка сервера", "model": error_schemas.InternalServerErrorResponse},
    },
)
async def update_response_status(
    response_uuid: UUID,
    data: ResponseUpdateStatusRequest,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> Response:
    return await ResponseService.update_status(user=user, response_uuid=response_uuid, data=data, session=session)


@router.delete(
    "/{response_uuid}",
    status_code=status.HTTP_200_OK,
    summary="Удалить отклик",
    description="Удаляет отклик. Доступно только администратору.",
    response_model=ResponseResponse,
)
async def delete_response(
    response_uuid: UUID,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> Response:
    return await ResponseService.delete(user=user, response_uuid=response_uuid, session=session)
