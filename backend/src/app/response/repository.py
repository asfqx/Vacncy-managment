from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.resume.models.resume import Resume
from app.vacancy.model import Vacancy

from .model import Response


class ResponseRepository:
    @staticmethod
    async def get(response_uuid: UUID, session: AsyncSession) -> Response | None:
        
        stmt = select(Response).where(Response.uuid == response_uuid)
        result = await session.execute(stmt)
        
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(session: AsyncSession) -> Sequence[Response]:
        
        stmt = select(Response).order_by(Response.created_at.desc())
        result = await session.execute(stmt)
        
        return result.scalars().all()

    @staticmethod
    async def get_by_candidate(candidate_id: UUID, session: AsyncSession) -> Sequence[Response]:
        
        stmt = (
            select(Response)
            .join(Resume, Resume.uuid == Response.resume_id)
            .where(Resume.user_id == candidate_id)
            .order_by(Response.created_at.desc())
        )
        result = await session.execute(stmt)
        
        return result.scalars().all()

    @staticmethod
    async def get_by_company(company_id: UUID, session: AsyncSession) -> Sequence[Response]:
        
        stmt = (
            select(Response)
            .join(Vacancy, Vacancy.uuid == Response.vacancy_id)
            .where(Vacancy.company_id == company_id)
            .order_by(Response.created_at.desc())
        )
        result = await session.execute(stmt)
        
        return result.scalars().all()

    @staticmethod
    async def get_by_resume_and_vacancy(
        resume_id: UUID,
        vacancy_id: UUID,
        session: AsyncSession,
    ) -> Response | None:
        
        stmt = select(Response).where(
            Response.resume_id == resume_id,
            Response.vacancy_id == vacancy_id,
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(response: Response, session: AsyncSession) -> Response:
        
        session.add(response)
        
        await session.commit()
        await session.refresh(response)
        
        return response

    @staticmethod
    async def update(response: Response, session: AsyncSession) -> Response:
        
        await session.commit()
        await session.refresh(response)
        
        return response

    @staticmethod
    async def delete(response: Response, session: AsyncSession) -> Response:
        
        await session.delete(response)
        await session.commit()
        
        return response
