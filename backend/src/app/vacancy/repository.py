from collections.abc import Callable, Sequence
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum import VacancyStatus

from .filter import VacancyFilterQueryParams
from .model import Vacancy
from .const import GENERIC_SEARCH_TERMS


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

        conditions: list[Any] = []

        for k, v in filters.items():
            if k not in filter_mapping or v is None:
                continue

            condition = filter_mapping[k](v)
            if condition is not None:
                conditions.append(condition)

        return conditions

    @staticmethod
    def _focused_query(raw_query: str) -> str:
        
        tokens = [token.strip().lower() for token in raw_query.split() if token.strip()]
        focused_tokens = [token for token in tokens if token not in GENERIC_SEARCH_TERMS]
        
        return " ".join(focused_tokens) or raw_query.strip()

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
    async def get_by_company(
        company_uuid: UUID,
        session: AsyncSession,
    ) -> Sequence[Vacancy]:
        
        stmt = select(Vacancy).where(Vacancy.company_id == company_uuid)
        result = await session.execute(stmt)
        
        return result.scalars().all()

    @staticmethod
    async def get_all(
        filters: VacancyFilterQueryParams,
        session: AsyncSession,
    ) -> Sequence[Vacancy]:
        
        stmt_filters = filters.model_dump(exclude_none=True)
        conditions = VacancyRepository._build_conditions(stmt_filters)

        stmt = select(Vacancy).where(*conditions)

        if filters.limit:
            stmt = stmt.limit(filters.limit + 1)

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

        raw_query = vacancy_name.strip()
        focused_query = VacancyRepository._focused_query(raw_query)

        normalized_query = func.lower(func.unaccent(raw_query))
        normalized_focused_query = func.lower(func.unaccent(focused_query))
        title_text = func.lower(func.unaccent(Vacancy.title))

        tsq_ru = func.websearch_to_tsquery("russian", func.unaccent(raw_query))
        tsq_en = func.websearch_to_tsquery("english", func.unaccent(raw_query))
        focused_tsq_ru = func.websearch_to_tsquery("russian", func.unaccent(focused_query))
        focused_tsq_en = func.websearch_to_tsquery("english", func.unaccent(focused_query))

        rank_ru = func.ts_rank_cd(Vacancy.search_vector, tsq_ru)
        rank_en = func.ts_rank_cd(Vacancy.search_vector, tsq_en)
        focused_rank_ru = func.ts_rank_cd(Vacancy.search_vector, focused_tsq_ru)
        focused_rank_en = func.ts_rank_cd(Vacancy.search_vector, focused_tsq_en)
        rank_trgm_title = func.similarity(title_text, normalized_query)
        focused_rank_trgm_title = func.similarity(title_text, normalized_focused_query)

        score = (
            func.greatest(rank_ru, rank_en) * 0.35
            + func.greatest(focused_rank_ru, focused_rank_en) * 1.15
            + (rank_trgm_title * 0.2)
            + (focused_rank_trgm_title * 0.7)
        ).label("score")

        stmt = (
            select(Vacancy, score)
            .where(*conditions)
            .where(
                or_(
                    Vacancy.search_vector.op("@@")(tsq_ru),
                    Vacancy.search_vector.op("@@")(tsq_en),
                    Vacancy.search_vector.op("@@")(focused_tsq_ru),
                    Vacancy.search_vector.op("@@")(focused_tsq_en),
                    rank_trgm_title > 0.2,
                    focused_rank_trgm_title > 0.2,
                )
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
    ) -> Vacancy:
        
        vacancy.status = VacancyStatus.BANNED

        await session.commit()
        await session.refresh(vacancy)

        return vacancy

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


