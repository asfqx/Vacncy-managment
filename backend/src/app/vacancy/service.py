from typing import Sequence
from uuid import UUID

from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.error_handler import handle_connection_errors, handle_model_errors
from app.users.model import User
from app.enum import UserRole

from .filter import VacancyFilterDepends
from .schema import VacancyUpdateRequest, VacancyCreateRequest
from .repository import VacancyRepository
from .model import Vacancy


class VacancyService:
    
    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def search(
        vacancy_name: str, 
        filters: VacancyFilterDepends, 
        session: AsyncSession,
    ) -> Sequence[Vacancy]:
        
        vacancies = await VacancyRepository.search(vacancy_name, filters, session)
        
        if not vacancies:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Вакансии не найдены",
            )
            
        return vacancies
    
    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get_all(
        session: AsyncSession,
    ) -> Sequence[Vacancy]:
        
        vacancies = await VacancyRepository.get_all(session)
        
        if not vacancies:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Вакансии не найдены",
            )
            
        return vacancies
    
    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def update(
        user_uuid: UUID,
        vacancy_uuid: UUID,
        data: VacancyUpdateRequest,
        session: AsyncSession,
    ) -> Vacancy:
        
        vacancy = await VacancyRepository.get(vacancy_uuid, session)
        
        if not vacancy:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Такой вакансии не существует",
            )
        
        if vacancy.company_id != user_uuid:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Вы не можете изменить эту вакансию",
            )
            
        return await VacancyRepository.update(vacancy, data, session)
    
    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def create(
        user: User,
        data: VacancyCreateRequest,
        session: AsyncSession,
    ) -> Vacancy:
        
        vacancy = await VacancyRepository.get_by_title(data.title, session)
        
        if vacancy:
            raise HTTPException(
                status.HTTP_409_CONFLICT,
                "Такая вакансия уже существует",
            )
        
        if user.role == UserRole.CANDIDATE:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "Вы не можете создать вакансию",
            )
            
        vacancy = Vacancy(
            title=data.title,
            description=data.description,
            company_id=user.uuid,
            city=data.city,
            remote=data.remote,
            salary=data.salary,
        )
            
        return await VacancyRepository.create(vacancy, session)
    