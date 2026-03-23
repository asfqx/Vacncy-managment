from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import Company
from .schema import CompanyUpdateRequest


class CompanyRepository:

    @staticmethod
    async def get(
        company_uuid: UUID,
        session: AsyncSession,
    ) -> Company | None:

        stmt = select(Company).where(Company.uuid == company_uuid)

        result = await session.execute(stmt)

        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_user(
        user_uuid: UUID,
        session: AsyncSession,
    ) -> Company | None:

        stmt = select(Company).where(Company.user_uuid == user_uuid)

        result = await session.execute(stmt)

        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_title(
        company_title: str,
        session: AsyncSession,
    ) -> Company | None:

        stmt = select(Company).where(Company.title == company_title)

        result = await session.execute(stmt)

        return result.scalar_one_or_none()

    @staticmethod
    async def get_all(
        session: AsyncSession,
    ) -> Sequence[Company]:
        
        stmt = select(Company)

        result = await session.execute(stmt)

        return result.scalars().all()

    @staticmethod
    async def delete(
        company: Company,
        session: AsyncSession,
    ) -> Company:

        await session.delete(company)
        await session.commit()

        return company

    @staticmethod
    async def create(
        company_obj: Company,
        session: AsyncSession,
    ) -> Company:

        session.add(company_obj)

        await session.commit()
        await session.refresh(company_obj)

        return company_obj

    @staticmethod
    async def update(
        company_obj: Company,
        new_data: CompanyUpdateRequest,
        session: AsyncSession,
    ) -> Company:

        update_dict = new_data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            if hasattr(company_obj, field):
                setattr(company_obj, field, value)

        await session.commit()
        await session.refresh(company_obj)

        return company_obj
