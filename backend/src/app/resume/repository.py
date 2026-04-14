from collections.abc import Callable, Sequence
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import and_, desc, exists, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.resume.filter import ResumeFilterQueryParams
from app.resume.models.education import ResumeEducation
from app.resume.models.expirience import ResumeExperience
from app.resume.models.resume import Resume
from app.search import SearchQueryBuilder


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
            "education_level": lambda v: exists(
                select(1)
                .select_from(ResumeEducation)
                .where(
                    ResumeEducation.resume_id == Resume.uuid,
                    ResumeEducation.level == v,
                )
            ),
        }

        conditions: list[Any] = []

        for k, v in filters.items():
            if k == "cursor_uuid":
                continue

            if k == "cursor":
                cursor_uuid = filters.get("cursor_uuid")
                if cursor_uuid is None:
                    conditions.append(Resume.created_at < v)
                else:
                    conditions.append(
                        or_(
                            Resume.created_at < v,
                            and_(Resume.created_at == v, Resume.uuid < cursor_uuid),
                        )
                    )
                continue

            if k in filter_mapping and v is not None:
                conditions.append(filter_mapping[k](v))

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
            .order_by(desc(Resume.created_at), desc(Resume.uuid))
            .distinct()
        )

        if filters.limit:
            stmt = stmt.limit(filters.limit)

        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def search(resume_name: str, filters: ResumeFilterQueryParams, session: AsyncSession) -> Sequence[Resume]:
        raw_query = resume_name.strip()
        if not raw_query:
            return await ResumeRepository.get_all(filters, session)

        stmt_filters = filters.model_dump(exclude_none=True)
        conditions, need_education_join = ResumeRepository._build_conditions(stmt_filters)

        search = SearchQueryBuilder.build(raw_query, Resume.title, Resume.search_vector)
        if search is None:
            return await ResumeRepository.get_all(filters, session)

        stmt = select(Resume, search.score)

        if need_education_join:
            stmt = stmt.join(ResumeEducation, ResumeEducation.resume_id == Resume.uuid)

        stmt = (
            stmt.where(*conditions)
            .where(search.match)
            .order_by(desc(Resume.created_at), desc(Resume.uuid), desc(search.score))
            .distinct()
            .limit(filters.limit or 50)
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
