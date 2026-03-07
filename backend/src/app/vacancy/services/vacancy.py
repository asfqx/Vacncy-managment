from typing import Sequence
from uuid import UUID

from fastapi import status, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.error_handler import handle_connection_errors, handle_model_errors
from app.users.model import User
from app.enum import UserRole
from app.vacancy.filter import VacancyFilterDepends, VacancyFilterQueryParams
from app.vacancy.schemas.vacancy import VacancyUpdateRequest, VacancyCreateRequest
from app.vacancy.repositories.vacancy import VacancyRepository
from app.vacancy.models.vacancy import Vacancy

from .search_request import SearchRequestService


class VacancyService:
    
    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def search(
        user_uuid: UUID,
        vacancy_name: str, 
        filters: VacancyFilterDepends, 
        background: BackgroundTasks,
        session: AsyncSession,
    ) -> Sequence[Vacancy]:
        
        vacancies = await VacancyRepository.search(vacancy_name, filters, session)
        
        if not vacancies:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Вакансии не найдены",
            )
            
        background.add_task(
            SearchRequestService.create,
            user_uuid,
            vacancy_name,
        )
        return vacancies
    
    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get_all(
        filters: VacancyFilterQueryParams,
        session: AsyncSession,
    ) -> Sequence[Vacancy]:
        
        vacancies = await VacancyRepository.get_all(filters, session)
        
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
    
    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get(
        vacancy_uuid: UUID,
        session: AsyncSession,
    ) -> Vacancy:
        
        vacancy = await VacancyRepository.get(vacancy_uuid, session)
        
        if not vacancy:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Такой вакансии не существует",
            )
        
        return vacancy
    