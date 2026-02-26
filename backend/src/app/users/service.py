from datetime import timedelta
from typing import Any
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.s3 import s3_adapter
from app.constant import AVATARS_BUCKET
from app.error_handler import handle_connection_errors, handle_model_errors
from app.users.dependency import AuthenticatedActiveUser
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
    async def update_bio(
        new_bio: UpdateUserProfileRequest,
        current_user: User,
        session: AsyncSession,
    ) -> dict[str, Any]:
        
        if new_bio.email and new_bio.email == current_user.email:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email уже используется",
            )

        exist_user = await UserRepository.get(current_user.uuid, session)

        if not exist_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )

        if new_bio.avatar_url:
            exists = s3_adapter.is_exists(AVATARS_BUCKET, new_bio.avatar_url)

            if not exists:
                raise HTTPException(
                    status.HTTP_400_BAD_REQUEST,
                    detail="Неправильный avatar_url",
                )

        updated_data = await UserRepository.update(exist_user, new_bio, session)

        ret: dict[str, Any] = {
            "username": updated_data.username,
            "email": updated_data.email,
            "avatar_url": updated_data.avatar_url,
        }

        return ret

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def upload_avatar(
        user: AuthenticatedActiveUser,
    ) -> dict[str, str]:

        url = s3_adapter.get_presigned_url(
            bucket_name=AVATARS_BUCKET,
            object_name=f"{user.uuid}/{uuid4()}.png",
            expires=timedelta(minutes=15),
        )

        return {"upload_url": url}
