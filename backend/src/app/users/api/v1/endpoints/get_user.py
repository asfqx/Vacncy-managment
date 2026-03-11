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
    response_model=GetUserProfileResponse,
    responses={
        401: {"model": error_schemas.UnauthorizedErrorResponse},
        404: {"model": error_schemas.NotFoundErrorResponse},
        429: {"model": RateLimitErrorResponse},
        500: {"model": error_schemas.InternalServerErrorResponse},
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
    response_model=UpdateUserProfileResponse,
    responses={
        401: {"model": error_schemas.UnauthorizedErrorResponse},
        404: {"model": error_schemas.NotFoundErrorResponse},
        409: {"model": error_schemas.AlreadyExistErrorResponse},
        429: {"model": RateLimitErrorResponse},
        500: {"model": error_schemas.InternalServerErrorResponse},
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
    response_model=CreatePreSignedURLResponse,
    responses={
        401: {"model": error_schemas.UnauthorizedErrorResponse},
        429: {"model": RateLimitErrorResponse},
    },
)
async def upload_avatar(
    user: AuthenticatedActiveUser,
) -> dict[str, str]:

    return await UserService.upload_avatar(user=user)