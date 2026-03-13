from datetime import datetime
from typing import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum import UserRole
from app.resume.filter import ResumeFilterQueryParams
from app.resume.models.resume import Resume
from app.resume.repository import ResumeRepository
from app.search_request.repository import SearchRequestRepository
from app.users.repository import UserRepository


class RecomendationService:
    @staticmethod
    async def recomendation(
        user_uuid: UUID,
        limit: int,
        session: AsyncSession,
        cursor: datetime | None,
    ) -> Sequence[Resume]:
        
        exist_user = await UserRepository.get(user_uuid, session)

        if not exist_user:
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден",
            )

        if exist_user.role == UserRole.CANDIDATE:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                detail="У пользователя нет прав на поиск резюме",
            )

        search_requests = await SearchRequestRepository.get_by_user(user_uuid, session)
        if not search_requests:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Поисковые запросы пользователя не найдены",
            )

        profile_query = " ".join(sr.request for sr in search_requests)
        filters = ResumeFilterQueryParams(limit=limit or 50, cursor=cursor)
        resumes = await ResumeRepository.search(profile_query, filters, session)

        if not resumes:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail="Резюме не найдены",
            )

        return resumes