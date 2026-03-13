from collections.abc import Callable, Sequence
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.resume.filter import ResumeFilterQueryParams
from app.resume.models.education import ResumeEducation
from app.resume.models.expirience import ResumeExperience
from app.resume.models.resume import Resume


class ResumeRepository:
    
    @staticmethod
    def _build_conditions(filters: dict[str, Any]) -> tuple[list[Any], bool]:
        
        need_education_join = filters.get("education_level") is not None

        filter_mapping: dict[str, Callable[[Any], Any]] = {
            "gender": lambda v: Resume.gender == v,
            "salary_from": lambda v: Resume.salary >= v,
            "salary_to": lambda v: Resume.salary <= v,
            "birth_date_from": lambda v: Resume.birth_date >= v,
            "birth_date_to": lambda v: Resume.birth_date <= v,
            "education_level": lambda v: ResumeEducation.level == v,
            "cursor": lambda v: Resume.created_at < v,
        }

        conditions = [
            filter_mapping[k](v)
            for k, v in filters.items()
            if k in filter_mapping and v is not None
        ]

        return conditions, need_education_join

    @staticmethod
    async def get(resume_uuid: UUID, session: AsyncSession) -> Resume | None:
        
        stmt = select(Resume).where(Resume.uuid == resume_uuid)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_user(user_uuid: UUID, session: AsyncSession) -> Resume | None:
        
        stmt = select(Resume).where(Resume.user_id == user_uuid)
        result = await session.execute(stmt)
        
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(filters: ResumeFilterQueryParams, session: AsyncSession) -> Sequence[Resume]:
        
        stmt_filters = filters.model_dump(exclude_none=True)
        conditions, need_education_join = ResumeRepository._build_conditions(stmt_filters)

        stmt = select(Resume)
        if need_education_join:
            stmt = stmt.join(ResumeEducation, ResumeEducation.resume_id == Resume.uuid)

        stmt = (
            stmt.where(*conditions)
            .order_by(desc(Resume.created_at))
            .distinct()
            .limit(filters.limit + 1 if filters.limit else 51)
        )

        result = await session.execute(stmt)
        
        return result.scalars().all()

    @staticmethod
    async def search(resume_name: str, filters: ResumeFilterQueryParams, session: AsyncSession) -> Sequence[Resume]:
        
        stmt_filters = filters.model_dump(exclude_none=True)
        conditions, need_education_join = ResumeRepository._build_conditions(stmt_filters)

        tsq_ru = func.websearch_to_tsquery("russian", func.unaccent(resume_name))
        tsq_en = func.websearch_to_tsquery("english", func.unaccent(resume_name))

        rank_ru = func.ts_rank_cd(Resume.search_vector, tsq_ru)
        rank_en = func.ts_rank_cd(Resume.search_vector, tsq_en)
        rank_trgm = func.similarity(Resume.title, resume_name)
        score = (func.greatest(rank_ru, rank_en) + (rank_trgm * 0.15)).label("score")

        stmt = select(Resume, score)
        
        if need_education_join:
            stmt = stmt.join(ResumeEducation, ResumeEducation.resume_id == Resume.uuid)

        stmt = (
            stmt.where(*conditions)
            .where(
                Resume.search_vector.op("@@")(tsq_ru)
                | Resume.search_vector.op("@@")(tsq_en)
                | (rank_trgm > 0.2)
            )
            .order_by(desc(score), desc(Resume.created_at))
            .distinct()
            .limit(filters.limit + 1 if filters.limit else 51)
        )

        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def create(resume_obj: Resume, session: AsyncSession) -> Resume:
        
        session.add(resume_obj)
        
        await session.commit()
        await session.refresh(resume_obj)
        
        return resume_obj

    @staticmethod
    async def update(resume_obj: Resume, new_data: BaseModel, session: AsyncSession) -> Resume:
        
        update_dict = new_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            if hasattr(resume_obj, field):
                setattr(resume_obj, field, value)

        await session.commit()
        await session.refresh(resume_obj)
        
        return resume_obj

    @staticmethod
    async def delete(resume_obj: Resume, session: AsyncSession) -> Resume:
        
        await session.delete(resume_obj)
        await session.commit()
        
        return resume_obj

    @staticmethod
    async def get_educations(resume_uuid: UUID, session: AsyncSession) -> Sequence[ResumeEducation]:
        
        stmt = (
            select(ResumeEducation)
            .where(ResumeEducation.resume_id == resume_uuid)
            .order_by(ResumeEducation.start_date.desc())
        )
        
        result = await session.execute(stmt)
        
        return result.scalars().all()

    @staticmethod
    async def get_education(education_uuid: UUID, session: AsyncSession) -> ResumeEducation | None:
        
        stmt = select(ResumeEducation).where(ResumeEducation.uuid == education_uuid)
        result = await session.execute(stmt)
        
        return result.scalar_one_or_none()

    @staticmethod
    async def create_education(education_obj: ResumeEducation, session: AsyncSession) -> ResumeEducation:
        
        session.add(education_obj)
        
        await session.commit()
        await session.refresh(education_obj)
        
        return education_obj

    @staticmethod
    async def delete_education(education_obj: ResumeEducation, session: AsyncSession) -> ResumeEducation:
        
        await session.delete(education_obj)
        await session.commit()
        
        return education_obj

    @staticmethod
    async def get_experiences(resume_uuid: UUID, session: AsyncSession) -> Sequence[ResumeExperience]:
        
        stmt = (
            select(ResumeExperience)
            .where(ResumeExperience.resume_id == resume_uuid)
            .order_by(ResumeExperience.start_date.desc())
        )
        result = await session.execute(stmt)
        
        return result.scalars().all()

    @staticmethod
    async def get_experience(experience_uuid: UUID, session: AsyncSession) -> ResumeExperience | None:
        
        stmt = select(ResumeExperience).where(ResumeExperience.uuid == experience_uuid)
        result = await session.execute(stmt)
        
        return result.scalar_one_or_none()

    @staticmethod
    async def create_experience(experience_obj: ResumeExperience, session: AsyncSession) -> ResumeExperience:
        
        session.add(experience_obj)
        
        await session.commit()
        await session.refresh(experience_obj)
        
        return experience_obj

    @staticmethod
    async def delete_experience(experience_obj: ResumeExperience, session: AsyncSession) -> ResumeExperience:
        
        await session.delete(experience_obj)
        await session.commit()
        
        return experience_obj
    