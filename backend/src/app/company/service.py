from uuid import UUID
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum import UserRole
from app.error_handler import handle_connection_errors, handle_model_errors
from app.users.model import User
from app.users.repository import UserRepository

from .model import Company
from .repository import CompanyRepository
from .schema import CompanyCreateRequest, CompanyUpdateRequest


class CompanyService:

    @staticmethod
    async def _serialize_company(
        company: Company,
        session: AsyncSession,
    ) -> dict[str, Any]:
        
        owner = await UserRepository.get(company.user_uuid, session)

        return {
            "uuid": company.uuid,
            "user_uuid": company.user_uuid,
            "title": company.title,
            "description": company.description,
            "company_size": company.company_size,
            "website": company.website,
            "avatar_url": owner.avatar_url if owner else None,
        }

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get_company(
        current_user: User,
        session: AsyncSession,
    ) -> dict[str, Any]:
        
        exist_user = await UserRepository.get(current_user.uuid, session)

        if not exist_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден ",
            )

        if exist_user.role == UserRole.CANDIDATE:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="У вас нет прав иметь вакансию",
            )

        company = await CompanyRepository.get_by_user(exist_user.uuid, session)

        if not company:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Компания не найдена",
            )

        return await CompanyService._serialize_company(company, session)

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get_company_by_user(
        current_user: User,
        user_uuid: UUID,
        session: AsyncSession,
    ) -> dict[str, Any]:
        
        if current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра компании пользователя",
            )

        company = await CompanyRepository.get_by_user(user_uuid, session)

        if not company:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Компания не найдена",
            )

        return await CompanyService._serialize_company(company, session)

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def update(
        new_bio: CompanyUpdateRequest,
        current_user: User,
        session: AsyncSession,
    ) -> dict[str, Any]:
        
        exist_user = await UserRepository.get(current_user.uuid, session)

        if not exist_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Пользователя не существует",
            )

        company = await CompanyRepository.get_by_user(current_user.uuid, session)

        if not company:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Компания не найдена",
            )

        if new_bio.title and new_bio.title != company.title:
            company_with_same_title = await CompanyRepository.get_by_title(new_bio.title, session)
            if company_with_same_title and company_with_same_title.uuid != company.uuid:
                raise HTTPException(
                    status.HTTP_409_CONFLICT,
                    detail="Компания с таким названием уже существует",
                )

        updated = await CompanyRepository.update(company, new_bio, session)

        return await CompanyService._serialize_company(updated, session)

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def create(
        user: User,
        data: CompanyCreateRequest,
        session: AsyncSession,
    ) -> dict[str, Any]:
        
        if user.role == UserRole.CANDIDATE:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="У вас нет прав создавать компанию",
            )

        existing_company_by_user = await CompanyRepository.get_by_user(user.uuid, session)
        if existing_company_by_user:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="У вас уже есть компания",
            )

        company_with_same_title = await CompanyRepository.get_by_title(data.title, session)
        if company_with_same_title:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                detail="Компания с таким названием уже существует",
            )

        company = Company(
            title=data.title,
            description=data.description or "",
            user_uuid=user.uuid,
            company_size=data.company_size or 0,
            website=data.website or "",
        )

        created = await CompanyRepository.create(company, session)

        return await CompanyService._serialize_company(created, session)

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get_company_by_id(
        company_id: UUID,
        session: AsyncSession,
    ) -> dict[str, Any]:
        
        company = await CompanyRepository.get(company_id, session)

        if not company:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Компания не найдена",
            )

        return await CompanyService._serialize_company(company, session)
