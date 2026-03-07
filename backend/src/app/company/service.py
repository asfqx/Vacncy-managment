from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.error_handler import handle_connection_errors, handle_model_errors
from app.users.model import User
from app.users.repository import UserRepository
from app.enum import UserRole

from .model import Company
from .repository import CompanyRepository
from .schema import CompanyUpdateRequest, CompanyCreateRequest


class CompanyService:

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get_company(
        current_user: User,
        session: AsyncSession,
    ) -> Company:

        exist_user = await UserRepository.get(current_user.uuid, session)

        if not exist_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )
            
        if exist_user.role == UserRole.CANDIDATE:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Пользователь не может иметь компанию",
            )
            
        company = await CompanyRepository.get_by_user(exist_user.uuid, session)
        
        if not company:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Компания не найдена",
            )
            
        return company

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def update(
        new_bio: CompanyUpdateRequest,
        current_user: User,
        session: AsyncSession,
    ) -> Company:

        exist_user = await UserRepository.get(current_user.uuid, session)

        if not exist_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )
            
        company = await CompanyRepository.get_by_user(current_user.uuid, session)

        if not company:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Компания не найдена",
            )

        return await CompanyRepository.update(company, new_bio, session)

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def create(
        user: User,
        data: CompanyCreateRequest,
        session: AsyncSession,
    ) -> Company:
        
        company = await CompanyRepository.get_by_title(data.title, session)
        
        if company:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Такая компания уже существует",
            )
        
        if user.role == UserRole.CANDIDATE:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Вы не можете создать компанию",
            )
            
        company = Company(
            title=data.title,
            description=data.description,
            user_uuid=user.uuid,
            company_size=data.company_size,
            websize=data.website,
        )
            
        return await CompanyRepository.create(company, session)
    
    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get_company_by_id(
        company_id: UUID, 
        session: AsyncSession,
    ) -> Company:
        
        company = await CompanyRepository.get(company_id, session)
        
        if not company:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Такой компании не существует",
            )
        
        return company
    