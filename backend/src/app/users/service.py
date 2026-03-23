from typing import Any, Sequence
from uuid import UUID, uuid4
from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.s3 import s3_adapter
from app.constant import AVATARS_BUCKET
from app.enum import UserRole
from app.error_handler import handle_connection_errors, handle_model_errors
from app.users.filter import UserFilterQueryParams
from app.users.model import User
from app.users.repository import UserRepository
from app.users.schema import UpdateUserProfileRequest


class UserService:
    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get_user_profile(
        current_user: User,
        session: AsyncSession,
    ) -> User:
        exist_user = await UserRepository.get(current_user.uuid, session)

        if not exist_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )

        return exist_user

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get_user_by_id(
        user_uuid: UUID,
        session: AsyncSession,
    ) -> User:
        exist_user = await UserRepository.get(user_uuid, session)

        if not exist_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )

        return exist_user

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get_all(
        current_user: User,
        filters: UserFilterQueryParams,
        session: AsyncSession,
    ) -> Sequence[User]:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра пользователей",
            )

        users = await UserRepository.get_all(filters, session)

        if not users:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Пользователи не найдены",
            )

        return users

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def delete(
        current_user: User,
        user_uuid: UUID,
        session: AsyncSession,
    ) -> None:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для блокировки пользователя",
            )

        if current_user.uuid == user_uuid:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Нельзя удалить самого себя",
            )

        exist_user = await UserRepository.get(user_uuid, session)

        if not exist_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )

        await UserRepository.ban(exist_user, session)

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def unban(
        current_user: User,
        user_uuid: UUID,
        session: AsyncSession,
    ) -> None:
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для разблокировки пользователя",
            )

        if current_user.uuid == user_uuid:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Нельзя изменить статус самого себя",
            )

        exist_user = await UserRepository.get(user_uuid, session)

        if not exist_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )

        await UserRepository.unban(exist_user, session)

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def update_bio(
        new_bio: UpdateUserProfileRequest,
        current_user: User,
        session: AsyncSession,
    ) -> dict[str, Any]:
        exist_user = await UserRepository.get(current_user.uuid, session)

        if not exist_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )

        if new_bio.email:
            normalized_email = new_bio.email.lower()

            if normalized_email != exist_user.email:
                user_with_same_email = await UserRepository.get_by_login(normalized_email, session)

                if user_with_same_email and user_with_same_email.uuid != exist_user.uuid:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Email уже существует",
                    )

                new_bio.email = normalized_email

        if new_bio.avatar_url:
            exists = s3_adapter.is_exists(AVATARS_BUCKET, new_bio.avatar_url)

            if not exists:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    detail="Передан некорректный avatar_url",
                )

        updated_data = await UserRepository.update(exist_user, new_bio, session)

        return {
            "username": updated_data.username,
            "email": updated_data.email,
            "fio": updated_data.fio,
            "avatar_url": updated_data.avatar_url,
            "telegram": updated_data.telegram,
            "phone_number": updated_data.phone_number,
        }

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def upload_avatar(
        user: User,
    ) -> dict[str, str]:
        url = s3_adapter.get_presigned_url(
            bucket_name=AVATARS_BUCKET,
            object_name=f"{user.uuid}/{uuid4()}.png",
            expires=timedelta(minutes=15),
        )

        return {"upload_url": url}
