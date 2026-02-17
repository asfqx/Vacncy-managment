from fastapi import APIRouter, BackgroundTasks, Request, Response, status

from app.auth.schemas import (
    CreateLoginRequest,
    CreateLoginResponse,
    CreateRegisterRequest,
)
from app.auth.services import AuthMailService, AuthService
from app.core import DBSession, RateLimitErrorResponse
from app.error_handler import error_schemas
from app.users.dependency import AuthenticatedActiveUser


router = APIRouter()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description=(
        "Создаёт нового пользователя по email и паролю. "
        "Email должен быть уникальным. Пароль сохраняется в хешированном виде.\n\n"
        "Параметры:\n"
        "- **email** — email нового пользователя.\n"
        "- **fio** — ФИО пользователя.\n"
        "- **username** — имя пользователя.\n "
        "- **password** — пароль пользователя."
    ),
    responses={
        201: {
            "description": "Пользователь успешно зарегистрирован",
        },
        409: {
            "description": "Пользователь уже существует",
            "model": error_schemas.AlreadyExistErrorResponse,
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
async def register(
    background: BackgroundTasks,
    register_data: CreateRegisterRequest,
    session: DBSession,
) -> None:

    await AuthService.register_user(
        email=register_data.email,
        username=register_data.username,
        password=register_data.password,
        role=register_data.role,
        fio=register_data.fio,
        background=background,
        session=session,
    )

    background.add_task(
        AuthMailService.send_welcome_mail,
        register_data.email,
        register_data.username,
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="Аутентификация пользователя",
    description=(
        "Авторизует пользователя по email и паролю. "
        "Возвращает access и refresh токен при успешной проверке учётных данных.\n\n"
        "Параметры:\n"
        "- **login** — логин пользователя.\n"
        "- **password** — пароль пользователя."
    ),
    response_model=CreateLoginResponse,
    responses={
        200: {
            "description": "Успешно выполнен вход",
            "model": CreateLoginResponse,
        },
        404: {
            "description": "Пользователь не найден",
            "model": error_schemas.NotFoundErrorResponse,
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
async def login(
    response: Response,
    login_data: CreateLoginRequest,
    session: DBSession,
) -> dict[str, str]:

    return await AuthService.login_user(
        login=login_data.login,
        password=login_data.password,
        response=response,
        session=session,
    )


@router.post(
    "/logout",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Выход пользователя из системы",
    description=(
        "Завершает сеанс пользователя, аннулируя access и refresh токены.\n\n"
    ),
    responses={
        202: {
            "description": "Успешно выполнен выход",
            "model": None,
        },
        400: {
            "description": "Пользователь не найден",
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
async def logout(
    user: AuthenticatedActiveUser,
    request: Request,
    response: Response,
    session: DBSession
) -> None:

    await AuthService.logout(user, request, response, session)
