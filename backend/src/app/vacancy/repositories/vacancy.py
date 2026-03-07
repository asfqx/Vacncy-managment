from collections.abc import Callable, Sequence
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum import VacancyStatus

from app.vacancy.filter import VacancyFilterQueryParams
from app.vacancy.models.vacancy import Vacancy


class VacancyRepository:

    @staticmethod
    def _build_conditions(filters: dict[str, Any]) -> list[Any]:

        filter_mapping: dict[str, Callable[[Any], Any]] = {
            "city": lambda v: Vacancy.city.ilike(f"%{v}%"),
            "company_id": lambda v: Vacancy.company_id == v,
            "salary_from": lambda v: Vacancy.salary >= v,
            "salary_to": lambda v: Vacancy.salary <= v,
            "remote": lambda v: Vacancy.remote.is_(v),
            "include_archived": lambda v: None if v else Vacancy.status == VacancyStatus.ACTIVE,
            "cursor": lambda v: Vacancy.created_at < v,
        }

        return [
            filter_mapping[k](v)
            for k, v in filters.items()
            if k in filter_mapping and v is not None
        ]
        
    @staticmethod
    async def get(
        vacancy_uuid: UUID,
        session: AsyncSession,
    ) -> Vacancy | None:

        stmt = select(Vacancy).where(Vacancy.uuid == vacancy_uuid)

        result = await session.execute(stmt)

        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_title(
        vacancy_title: str,
        session: AsyncSession,
    ) -> Vacancy | None:

        stmt = select(Vacancy).where(Vacancy.title == vacancy_title)

        result = await session.execute(stmt)

        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all(
        filters: VacancyFilterQueryParams,
        session: AsyncSession,
    ) -> Sequence[Vacancy]:
        
        stmt_filters = filters.model_dump(exclude_none=True)
        conditions = VacancyRepository._build_conditions(stmt_filters)

        stmt = (
            select(Vacancy)
            .where(*conditions)
            .limit(filters.limit + 1 if filters.limit else 51)
        )

        result = await session.execute(stmt)

        return result.scalars().all()

    @staticmethod
    async def search(
        vacancy_name: str,
        filters: VacancyFilterQueryParams,
        session: AsyncSession,
    ) -> Sequence[Vacancy]:

        stmt_filters = filters.model_dump(exclude_none=True)
        conditions = VacancyRepository._build_conditions(stmt_filters)
        
        tsq_ru = func.websearch_to_tsquery("russian", func.unaccent(vacancy_name))
        tsq_en = func.websearch_to_tsquery("english", func.unaccent(vacancy_name))

        rank_ru = func.ts_rank_cd(Vacancy.search_vector, tsq_ru)
        rank_en = func.ts_rank_cd(Vacancy.search_vector, tsq_en)

        rank_trgm = func.similarity(Vacancy.title, vacancy_name)

        score = (func.greatest(rank_ru, rank_en) + (rank_trgm * 0.15)).label("score")

        stmt = (
            select(Vacancy, score)
            .where(*conditions)
            .where(
                Vacancy.search_vector.op("@@")(tsq_ru)
                | Vacancy.search_vector.op("@@")(tsq_en)
                | (rank_trgm > 0.2)
            )
            .order_by(desc(score), desc(Vacancy.created_at))
            .limit(filters.limit + 1 if filters.limit else 51)
        )

        result = await session.execute(stmt)
                
        return result.scalars().all()

    @staticmethod
    async def delete(
        vacancy: Vacancy,
        session: AsyncSession,
    ) -> Vacancy:

        await session.delete(vacancy)
        await session.commit()

        return vacancy
    
    @staticmethod
    async def soft_delete(
        vacancy: Vacancy,
        session: AsyncSession,
    ) -> None:

        vacancy.status = VacancyStatus.BANNED
        
        await session.commit()

    @staticmethod
    async def create(
        vacancy_obj: Vacancy,
        session: AsyncSession,
    ) -> Vacancy:

        session.add(vacancy_obj)

        await session.commit()
        await session.refresh(vacancy_obj)

        return vacancy_obj

    @staticmethod
    async def update(
        vacancy_obj: Vacancy,
        new_data: BaseModel,
        session: AsyncSession,
    ) -> Vacancy:

        update_dict = new_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            if hasattr(vacancy_obj, field):
                setattr(vacancy_obj, field, value)

        await session.commit()
        await session.refresh(vacancy_obj)

        return vacancy_obj
