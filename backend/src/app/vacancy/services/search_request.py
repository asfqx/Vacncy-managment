from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.error_handler import handle_connection_errors, handle_model_errors
from app.users.model import User
from app.users.repository import UserRepository
from app.enum import UserRole
from app.core import AsyncSessionLocal

from app.vacancy.models.search_request import SearchRequest
from app.vacancy.repositories.search_request import SearchRequestRepository


class SearchRequestService:

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get_all(
        user_uuid: UUID,
        user: User,
        session: AsyncSession,
    ) ->  Sequence[SearchRequest]:

        exist_user = await UserRepository.get(user_uuid, session)

        if not exist_user:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден",
            )
            
        if user.role != UserRole.ADMIN:
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
    async def create(
        user_uuid: UUID,
        request: str,
    ) -> SearchRequest:
            
        search_request = SearchRequest(
            user_uuid=user_uuid,
            request=request,
        )
        
        async with AsyncSessionLocal() as session:
            return await SearchRequestRepository.create(search_request, session)
    
    
    