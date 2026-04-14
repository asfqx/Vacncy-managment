from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, status

from app.core import DBSession, RateLimitErrorResponse
from app.error_handler import error_schemas
from app.resume.filter import ResumeFilterDepends
from app.resume.models import ResumeEducation, ResumeExperience
from app.resume.schemas.resume import (
    ResumeEducationCreateRequest,
    ResumeEducationResponse,
    ResumeExperienceCreateRequest,
    ResumeExperienceResponse,
    ResumeResponse,
    ResumeUpsertRequest,
)
from app.resume.services.recommendation import RecomendationService
from app.resume.services.resume import ResumeService
from app.users.dependency import AuthenticatedActiveUser


router = APIRouter()



@router.delete(
    "/{resume_uuid}",
    status_code=status.HTTP_200_OK,
    summary="Удалить резюме",
    description="Удаляет резюме по UUID. Владелец может удалить свое резюме, администратор — любое.",
    response_model=ResumeResponse,
)
async def delete_resume(
    resume_uuid: UUID,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> ResumeResponse:
    resume = await ResumeService.delete_resume(user=user, resume_uuid=resume_uuid, session=session)
    return await ResumeService.build_response(resume, session)

@router.post(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Создать или обновить мое резюме",
    description=(
        "Создает новое резюме пользователя или обновляет уже существующее. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=ResumeResponse,
    responses={
        200: {
            "description": "Резюме успешно сохранено",
            "model": ResumeResponse,
        },
        400: {
            "description": "Переданы некорректные данные резюме",
            "model": error_schemas.BadRequestErrorResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Пользователь или резюме не найдены",
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
async def upsert_resume(
    data: ResumeUpsertRequest,
    user: AuthenticatedActiveUser,
    sesssion: DBSession,
) -> ResumeResponse:
    return await ResumeService.upsert_my_resume(user=user, data=data, session=sesssion)


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Получить список резюме",
    description=(
        "Возвращает список резюме с учетом фильтров и курсорной пагинации. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=list[ResumeResponse],
    responses={
        200: {
            "description": "Список резюме успешно получен",
            "model": list[ResumeResponse],
        },
        400: {
            "description": "Переданы некорректные параметры фильтрации",
            "model": error_schemas.BadRequestErrorResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Резюме не найдены",
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
async def get_all_resumes(
    user: AuthenticatedActiveUser,
    filters: ResumeFilterDepends,
    sesssion: DBSession,
) -> list[ResumeResponse]:
    return await ResumeService.get_all(user=user, filters=filters, session=sesssion)


@router.get(
    "/search",
    status_code=status.HTTP_200_OK,
    summary="Поиск резюме",
    description=(
        "Выполняет поиск резюме по строке запроса и фильтрам. "
        "История поиска используется в дальнейшем для рекомендаций. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=list[ResumeResponse],
    responses={
        200: {
            "description": "Результаты поиска резюме успешно получены",
            "model": list[ResumeResponse],
        },
        400: {
            "description": "Переданы некорректные параметры поиска",
            "model": error_schemas.BadRequestErrorResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Подходящие резюме не найдены",
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
async def search_resumes(
    user: AuthenticatedActiveUser,
    resume_title: str,
    filters: ResumeFilterDepends,
    background: BackgroundTasks,
    sesssion: DBSession,
) -> list[ResumeResponse]:
    return await ResumeService.search(
        user=user,
        resume_title=resume_title,
        filters=filters,
        background=background,
        session=sesssion,
    )


@router.get(
    "/recommendation",
    status_code=status.HTTP_200_OK,
    summary="Получить рекомендации по резюме",
    description=(
        "Возвращает список рекомендованных резюме на основе поисковой истории работодателя. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=list[ResumeResponse],
    responses={
        200: {
            "description": "Рекомендации по резюме успешно получены",
            "model": list[ResumeResponse],
        },
        400: {
            "description": "Переданы некорректные параметры запроса",
            "model": error_schemas.BadRequestErrorResponse,
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
    session: DBSession,
    limit: int = 50,
    cursor: datetime | None = None,
    cursor_uuid: UUID | None = None,
) -> list[ResumeResponse]:
    resumes = await RecomendationService.recomendation(
        user_uuid=user.uuid,
        limit=limit,
        cursor=cursor,
        cursor_uuid=cursor_uuid,
        session=session,
    )

    return [await ResumeService.build_response(item, session) for item in resumes]


@router.get(
    "/me",
    status_code=status.HTTP_200_OK,
    summary="Получить мое резюме",
    description=(
        "Возвращает полное резюме текущего авторизованного пользователя вместе с образованием и опытом работы. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=ResumeResponse,
    responses={
        200: {
            "description": "Резюме пользователя успешно получено",
            "model": ResumeResponse,
        },
        400: {
            "description": "Переданы некорректные параметры запроса",
            "model": error_schemas.BadRequestErrorResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Резюме пользователя не найдено",
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
async def get_my_resume(
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> ResumeResponse:
    return await ResumeService.get_my_resume(user=user, session=session)


@router.get(
    "/{resume_uuid}",
    status_code=status.HTTP_200_OK,
    summary="Получить резюме по UUID",
    description=(
        "Возвращает полную информацию о резюме по UUID, включая образование и опыт работы. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=ResumeResponse,
    responses={
        200: {
            "description": "Резюме успешно получено",
            "model": ResumeResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        404: {
            "description": "Резюме не найдено",
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
async def get_resume(
    resume_uuid: UUID,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> ResumeResponse:
    return await ResumeService.get(resume_uuid=resume_uuid, session=session)



@router.delete(
    "/{resume_uuid}",
    status_code=status.HTTP_200_OK,
    summary="Удалить резюме",
    description="Удаляет резюме по UUID. Владелец может удалить свое резюме, администратор — любое.",
    response_model=ResumeResponse,
)
async def delete_resume(
    resume_uuid: UUID,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> ResumeResponse:
    resume = await ResumeService.delete_resume(user=user, resume_uuid=resume_uuid, session=session)
    return await ResumeService.build_response(resume, session)

@router.post(
    "/{resume_uuid}/educations",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить образование в резюме",
    description=(
        "Создает новую запись об образовании в указанном резюме. "
        "Требуется JWT access-токен в заголовке Authorization. "
        "Пользователь может изменять только собственное резюме."
    ),
    response_model=ResumeEducationResponse,
    responses={
        201: {
            "description": "Образование успешно добавлено",
            "model": ResumeEducationResponse,
        },
        400: {
            "description": "Переданы некорректные данные образования",
            "model": error_schemas.BadRequestErrorResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        403: {
            "description": "Недостаточно прав для изменения резюме",
            "model": error_schemas.ForbiddenErrorResponse,
        },
        404: {
            "description": "Резюме не найдено",
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
async def create_education(
    resume_uuid: UUID,
    data: ResumeEducationCreateRequest,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> ResumeEducation:
    return await ResumeService.create_education(
        user=user,
        resume_uuid=resume_uuid,
        data=data,
        session=session,
    )


@router.delete(
    "/{resume_uuid}/educations/{education_uuid}",
    status_code=status.HTTP_200_OK,
    summary="Удалить образование из резюме",
    description=(
        "Удаляет запись об образовании из указанного резюме. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=ResumeEducationResponse,
    responses={
        200: {
            "description": "Образование успешно удалено",
            "model": ResumeEducationResponse,
        },
        400: {
            "description": "Переданы некорректные параметры удаления",
            "model": error_schemas.BadRequestErrorResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        403: {
            "description": "Недостаточно прав для изменения резюме",
            "model": error_schemas.ForbiddenErrorResponse,
        },
        404: {
            "description": "Резюме или образование не найдены",
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
async def delete_education(
    resume_uuid: UUID,
    education_uuid: UUID,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> ResumeEducation:
    return await ResumeService.delete_education(
        user=user,
        resume_uuid=resume_uuid,
        education_uuid=education_uuid,
        session=session,
    )



@router.delete(
    "/{resume_uuid}",
    status_code=status.HTTP_200_OK,
    summary="Удалить резюме",
    description="Удаляет резюме по UUID. Владелец может удалить свое резюме, администратор — любое.",
    response_model=ResumeResponse,
)
async def delete_resume(
    resume_uuid: UUID,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> ResumeResponse:
    resume = await ResumeService.delete_resume(user=user, resume_uuid=resume_uuid, session=session)
    return await ResumeService.build_response(resume, session)

@router.post(
    "/{resume_uuid}/experiences",
    status_code=status.HTTP_201_CREATED,
    summary="Добавить опыт работы в резюме",
    description=(
        "Создает новую запись об опыте работы в указанном резюме. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=ResumeExperienceResponse,
    responses={
        201: {
            "description": "Опыт работы успешно добавлен",
            "model": ResumeExperienceResponse,
        },
        400: {
            "description": "Переданы некорректные данные опыта работы",
            "model": error_schemas.BadRequestErrorResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        403: {
            "description": "Недостаточно прав для изменения резюме",
            "model": error_schemas.ForbiddenErrorResponse,
        },
        404: {
            "description": "Резюме не найдено",
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
async def create_experience(
    resume_uuid: UUID,
    data: ResumeExperienceCreateRequest,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> ResumeExperience:
    return await ResumeService.create_experience(
        user=user,
        resume_uuid=resume_uuid,
        data=data,
        session=session,
    )


@router.delete(
    "/{resume_uuid}/experiences/{experience_uuid}",
    status_code=status.HTTP_200_OK,
    summary="Удалить опыт работы из резюме",
    description=(
        "Удаляет запись об опыте работы из указанного резюме. "
        "Требуется JWT access-токен в заголовке Authorization."
    ),
    response_model=ResumeExperienceResponse,
    responses={
        200: {
            "description": "Опыт работы успешно удален",
            "model": ResumeExperienceResponse,
        },
        400: {
            "description": "Переданы некорректные параметры удаления",
            "model": error_schemas.BadRequestErrorResponse,
        },
        401: {
            "description": "Пользователь не авторизован",
            "model": error_schemas.UnauthorizedErrorResponse,
        },
        403: {
            "description": "Недостаточно прав для изменения резюме",
            "model": error_schemas.ForbiddenErrorResponse,
        },
        404: {
            "description": "Резюме или опыт работы не найдены",
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
async def delete_experience(
    resume_uuid: UUID,
    experience_uuid: UUID,
    user: AuthenticatedActiveUser,
    session: DBSession,
) -> ResumeExperience:
    return await ResumeService.delete_experience(
        user=user,
        resume_uuid=resume_uuid,
        experience_uuid=experience_uuid,
        session=session,
    )

