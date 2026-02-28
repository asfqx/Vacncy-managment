from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.error_handler import handle_connection_errors, handle_model_errors
from app.users.model import User
from app.users.repository import UserRepository
from app.enum import UserRole

from .model import SearchRequest
from .repository import SearchRequestRepository
from .schema import SearchRequestCreateRequest


class CompanyService:

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get_all(
        current_user: User,
        session: AsyncSession,
    ) ->  Sequence[SearchRequest]:

        exist_user = await UserRepository.get(current_user.uuid, session)

        if not exist_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )
            
        if exist_user.role != UserRole.ADMIN:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Пользователь не имеет прав",
            )
            
        requests = await SearchRequestRepository.get_all(session)
        
        if not requests:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Запросы не найдены",
            )
            
        return requests
    
    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get_by_user(
        current_user: User,
        session: AsyncSession,
    ) -> Sequence[SearchRequest]:

        exist_user = await UserRepository.get(current_user.uuid, session)

        if not exist_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )
            
        if exist_user.role == UserRole.ADMIN:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="Пользователь не имеет прав",
            )
        
        requests = await SearchRequestRepository.get_by_user(
            exist_user.uuid, 
            session,
        )
        
        if not requests:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Запросы не найдены",
            )
            
        return requests

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def create(
        user: User,
        data: SearchRequestCreateRequest,
        session: AsyncSession,
    ) -> SearchRequest:
        
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
    
