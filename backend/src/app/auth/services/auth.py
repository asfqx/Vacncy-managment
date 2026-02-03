import datetime as dt
from typing import Any
from uuid import UUID

from fastapi import HTTPException, Request, Response, status, BackgroundTasks
from jose import JWTError
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.cache import BaseCacheAdapter, RedisAdapter
from app.auth.schemas.auth import CreateSuperuserRequest
from app.core import DBSession, settings
from app.enum import UserRole
from app.error_handler import (
    handle_connection_errors,
    handle_model_errors,
)
from app.security import Argon2Hasher, JWTUtils
from app.users.model import User
from app.users.repository import UserRepository

from .token import JWTTokenService


class AuthService:

    cache: BaseCacheAdapter = RedisAdapter(settings.cache_url)

    @staticmethod
    @handle_connection_errors
    @handle_model_errors
    async def create_superuser(
        data: CreateSuperuserRequest,
        session: AsyncSession
    ) -> None:

        logger.info("Создание суперпользователя")

        user = User(
            password_hash=Argon2Hasher.hash(data.password),
            email=data.email,
            fio=data.fio,
            telegram_link=data.telegram_link,
            username=data.username,
            role=UserRole.ADMIN,
        )

        await UserRepository.create(user, session)

        logger.success("Суперпользователь создан")

    @staticmethod
    @handle_connection_errors
    @handle_model_errors
    async def register_user(
        email: str,
        username: str,
        password: str,
        fio: str,
        telegram_link: str,
        background: BackgroundTasks,
        session: AsyncSession,
    ) -> None:

        email_user = await UserRepository.get_by_login(email, session)
        username_user = await UserRepository.get_by_login(username, session)

        if email_user or username_user:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="Пользователь с таким email или username уже существует"
            )

        user = User(
            password_hash=Argon2Hasher.hash(password),
            email=email.lower(),
            username=username,
            fio=fio,
            telegram_link=telegram_link,
        )

        await UserRepository.create(user, session)

        await EmailConfirmService.send_token(email, background, session)


    @staticmethod
    @handle_connection_errors
    @handle_model_errors
    async def login_user(
        login: str,
        password: str,
        session: AsyncSession,
        response: Response,
    ) -> dict[str, str]:

        logger.info("Начинаем аутентификацию пользователя.")

        exist_user = await UserRepository.get_by_login(login, session)

        if not exist_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )

        if not Argon2Hasher.verify(password, exist_user.password_hash): # type: ignore
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Неверный пароль",
            )
        
        if not exist_user.email_confirmed and exist_user.role is not UserRole.ADMIN:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не подтвердил свою почту",
            )

        logger.info("Генерируем токен для пользователя")

        access_token = JWTTokenService.create_access_token(
            exist_user.uuid,
            exist_user.role,
        )

        response.headers['Authorization'] = access_token

        refresh_token = JWTTokenService.create_refresh_token(
            exist_user.uuid,
            exist_user.role,
        )

        response.set_cookie(
            key="refreshtoken",
            value=refresh_token,
            max_age=60 * 60 * 24 * 60,  # 60 дней
            path=settings.api_prefix,
            secure=not settings.debug,
            httponly=True,
            samesite="strict",
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }



    @classmethod
    @handle_connection_errors
    @handle_model_errors
    async def logout(
        cls,
        user: User,
        request: Request,
        response: Response,
        session: AsyncSession,
    ) -> None:

        token = request.cookies.get("refreshtoken")

        if not token:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Отсутсвтвует refresh_token в cookie",
            )

        payload = JWTUtils.decode(token)

        response.delete_cookie(
            key="refreshtoken",
            path="/api/v1/auth",
            secure=not settings.debug,
            httponly=True,
            samesite="strict",
        )

        del response.headers['Authorization']

        jti = payload["jti"]
        expire = payload["exp"]

        now_ts = int(dt.datetime.now(dt.UTC).timestamp())
        ttl = expire - now_ts

        await cls.cache.set(
            f"blacklist:{jti}",
            "1",
            expire=ttl,
        )

    @classmethod
    @handle_connection_errors
    @handle_model_errors
    async def refresh_token(
        cls,
        refresh_token: str,
        user: User,
        response: Response,
        session: AsyncSession,
    ) -> dict[str, Any]:

        try:
            payload = JWTUtils.decode(refresh_token)
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный refresh токен",
            ) from e

        user_uuid = payload["sub"]
        jti = payload["jti"]

        is_blacklisted = await cls.cache.get(f"blacklist:{jti}")

        if is_blacklisted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен отозван",
            )

        access_token = JWTTokenService.create_access_token(
            user_uuid,
            user.role,
        )

        response.headers['Authorization'] = access_token

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    @staticmethod
    async def get_role_from_jwt(
        access_token: str,
        session: DBSession,
    ) -> dict[str, Any]:

        uuid = JWTTokenService.get_uuid_from_token(access_token)

        user = await UserRepository.get(UUID(uuid), session)

        if user is None:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )

        return {
            "role": user.role,
        }
