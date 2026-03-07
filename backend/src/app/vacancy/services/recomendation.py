from uuid import UUID
from typing import Sequence
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status, HTTPException

from app.vacancy.models.vacancy import Vacancy
from app.vacancy.repositories.vacancy import VacancyRepository
from app.vacancy.repositories.search_request import SearchRequestRepository
from app.users.repository import UserRepository
from app.vacancy.filter import VacancyFilterQueryParams
from app.enum import UserRole


class RecomendationService:
    
    @staticmethod
    async def recomendation(
        user_uuid: UUID, 
        limit: int,
        session: AsyncSession,
        cursor: datetime | None,
    ) -> Sequence[Vacancy]:
        
        exist_user = await UserRepository.get(user_uuid, session)

        if not exist_user:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден",
            )
        
        if exist_user.role == UserRole.COMPANY:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="У пользователя нету прав",
            )
        
        search_requests = await SearchRequestRepository.get_by_user(
            user_uuid,
            session,
        )
        
        if not search_requests:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Запросов пользователя не найдено",
            )
            
        profile_query = " ".join(sr.request for sr in search_requests)
        
        filters = VacancyFilterQueryParams(limit=limit or 50, cursor=cursor)
        
        vacancies = await VacancyRepository.search(profile_query, filters, session)
        
        if not search_requests:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Вакансий не найдено",
            )
        
        return vacancies
        