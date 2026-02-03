from loguru import logger
from sqlalchemy.exc import IntegrityError

from app.auth.schemas.auth import CreateSuperuserRequest
from app.auth.services import AuthService
from app.core import settings
from app.core.db import AsyncSessionLocal
from app.users.repository import UserRepository


async def create_first_superuser() -> None:

    if not (settings.first_superuser_email and settings.first_superuser_password):
        logger.warning(
            "Не заданы параметры для создания суперпользователя. Пропускаем..."
        )
        return

    register_data = CreateSuperuserRequest(
        email=settings.first_superuser_email,
        username=settings.first_superuser_username,
        password=settings.first_superuser_password,
        fio=settings.first_superuser_fio,
        telegram_link=settings.first_superuser_telegram_link,
    )

    async with AsyncSessionLocal() as session:
        existing_user = await UserRepository.get_by_login(
            register_data.email,
            session=session,
        )
        if existing_user:
            logger.info("Суперпользователь уже существует")
            return

        try:
            await AuthService.create_superuser(data=register_data, session=session)
            logger.success(
                f"Суперпользователь создан успешно: email={register_data.email}, username={register_data.username}"
            )
        except IntegrityError:
            await session.rollback()
            logger.error(
                "Ошибка БД при создании суперпользователя (возможно, дублирование)",
            )
