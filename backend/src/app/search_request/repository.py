from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .model import SearchRequest


class SearchRequestRepository:
    

    @staticmethod
    async def get(
        search_uuid: UUID,
        session: AsyncSession,
    ) -> SearchRequest | None:

        stmt = select(SearchRequest).where(SearchRequest.uuid == search_uuid)

        result = await session.execute(stmt)

        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_user(
        user_uuid: UUID,
        session: AsyncSession,
        limit: int = 3,
    ) -> Sequence[SearchRequest]:

        stmt = (
            select(SearchRequest)
            .where(SearchRequest.user_uuid == user_uuid)
            .order_by(SearchRequest.created_at.desc())
            .limit(limit)
        )
        result = await session.execute(stmt)

        return result.scalars().all()
    
    @staticmethod
    async def get_all(
        session: AsyncSession,
    ) -> Sequence[SearchRequest]:
        
        stmt = select(SearchRequest)

        result = await session.execute(stmt)

        return result.scalars().all()

    @staticmethod
    async def create(
        search_request: SearchRequest,
        session: AsyncSession,
    ) -> SearchRequest:

        session.add(search_request)

        await session.commit()
        await session.refresh(search_request)

        return search_request
