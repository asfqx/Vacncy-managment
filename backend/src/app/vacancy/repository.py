from collections.abc import Callable, Sequence
from typing import Any
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum import VacancyStatus
from app.search import SearchQueryBuilder

from .filter import VacancyFilterQueryParams
from .model import Vacancy


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
        }

        conditions: list[Any] = []

        for k, v in filters.items():
            if k == "cursor_uuid":
                continue

            if k == "cursor":
                cursor_uuid = filters.get("cursor_uuid")
                if cursor_uuid is None:
                    conditions.append(Vacancy.created_at < v)
                else:
                    conditions.append(
                        or_(
                            Vacancy.created_at < v,
                            and_(Vacancy.created_at == v, Vacancy.uuid < cursor_uuid),
                        )
                    )
                continue

            if k not in filter_mapping or v is None:
                continue

            condition = filter_mapping[k](v)
            if condition is not None:
                conditions.append(condition)

        return conditions

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

        stmt = (
            select(Vacancy)
            .where(*conditions)
            .order_by(desc(Vacancy.created_at), desc(Vacancy.uuid))
        )

        if filters.limit:
            stmt = stmt.limit(filters.limit)

        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def search(
        vacancy_name: str,
        filters: VacancyFilterQueryParams,
        session: AsyncSession,
    ) -> Sequence[Vacancy]:

        raw_query = vacancy_name.strip()
        if not raw_query:
            return await VacancyRepository.get_all(filters, session)

        stmt_filters = filters.model_dump(exclude_none=True)
        conditions = VacancyRepository._build_conditions(stmt_filters)

        search = SearchQueryBuilder.build(raw_query, Vacancy.title, Vacancy.search_vector)
        if search is None:
            return await VacancyRepository.get_all(filters, session)

        stmt = (
            select(Vacancy, search.score)
            .where(*conditions)
            .where(search.match)
            .order_by(desc(Vacancy.created_at), desc(Vacancy.uuid), desc(search.score))
            .limit(filters.limit or 50)
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
