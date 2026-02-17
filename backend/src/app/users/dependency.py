import datetime as dt
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.constant import ALGORITHM
from app.core import DBSession, settings
from app.enum import UserRole, UserStatus
from app.users.model import User
from app.users.repository import UserRepository


security = HTTPBearer(bearerFormat="JWT", scheme_name="Authorization")


async def get_current_user(
    session: DBSession,
    token_credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> User:

    token = token_credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.hash_secret_key,
            algorithms=ALGORITHM,
        )

    except JWTError:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось декодировать переданный токен",
        ) from JWTError

    uuid = payload.get("sub")

    if uuid is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            detail="Переданный токен неверный или истек",
        )

    exp = payload.get("exp")

    if not exp or dt.datetime.now(dt.UTC).timestamp() > exp:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Переданный токен истек",
        )

    user = await UserRepository.get(uuid, session)

    if not user:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    return user


UserDepends = Depends(get_current_user)
AuthenticatedUser = Annotated[User, UserDepends]


async def get_current_active_user(
    user: Annotated[User, Depends(get_current_user)],
) -> User:

    if user.status.upper() != UserStatus.ACTIVE:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Пользователь заблокирован",
        )

    return user


ActiveUserDepends = Depends(get_current_active_user)
AuthenticatedActiveUser = Annotated[User, ActiveUserDepends]


async def get_current_admin(
    user: Annotated[User, Depends(get_current_user)],
) -> User:

    if user.role.upper() != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь не является администратором",
        )

    return user


AdminUser = Depends(get_current_admin)
