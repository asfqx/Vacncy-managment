from uuid import UUID

from fastapi import BackgroundTasks, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.enum import UserRole
from app.error_handler import handle_connection_errors, handle_model_errors
from app.resume.filter import ResumeFilterQueryParams
from app.resume.models.education import ResumeEducation
from app.resume.models.expirience import ResumeExperience
from app.resume.models.resume import Resume
from app.resume.repository import ResumeRepository
from app.resume.schemas.resume import (
    ResumeEducationCreateRequest,
    ResumeEducationResponse,
    ResumeExperienceCreateRequest,
    ResumeExperienceResponse,
    ResumeResponse,
    ResumeUpsertRequest,
)
from app.search_request.service import SearchRequestService
from app.users.model import User


class ResumeService:
    
    @staticmethod
    async def build_response(resume: Resume, session: AsyncSession) -> ResumeResponse:
        
        educations = await ResumeRepository.get_educations(resume.uuid, session)
        experiences = await ResumeRepository.get_experiences(resume.uuid, session)

        return ResumeResponse(
            uuid=resume.uuid,
            title=resume.title,
            about_me=resume.about_me,
            user_id=resume.user_id,
            salary=resume.salary,
            currency=resume.currency,
            gender=resume.gender,
            birth_date=resume.birth_date,
            created_at=resume.created_at,
            updated_at=resume.updated_at,
            educations=[ResumeEducationResponse.model_validate(item) for item in educations],
            experiences=[ResumeExperienceResponse.model_validate(item) for item in experiences],
        )

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def upsert_my_resume(
        user: User,
        data: ResumeUpsertRequest,
        session: AsyncSession,
    ) -> ResumeResponse:

        if user.role == UserRole.COMPANY:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "РЈ РІР°СЃ РЅРµС‚ РїСЂР°РІ РёРјРµС‚СЊ СЂРµР·СЋРјРµ",
            )

        resume = await ResumeRepository.get_by_user(user.uuid, session)
        if resume:
            resume = await ResumeRepository.update(resume, data, session)
        else:
            resume = Resume(
                title=data.title,
                about_me=data.about_me,
                user_id=user.uuid,
                salary=data.salary,
                currency=data.currency,
                gender=data.gender,
                birth_date=data.birth_date,
            )
            resume = await ResumeRepository.create(resume, session)

        return await ResumeService.build_response(resume, session)

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get_my_resume(user: User, session: AsyncSession) -> ResumeResponse:
        
        if user.role == UserRole.COMPANY:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "РЈ РІР°СЃ РЅРµС‚ РїСЂР°РІ РёРјРµС‚СЊ СЂРµР·СЋРјРµ",
            )

        resume = await ResumeRepository.get_by_user(user.uuid, session)
        
        if not resume:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Р РµР·СЋРјРµ РЅРµ РЅР°Р№РґРµРЅРѕ",
            )

        return await ResumeService.build_response(resume, session)

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get(resume_uuid: UUID, session: AsyncSession) -> ResumeResponse:
        
        resume = await ResumeRepository.get(resume_uuid, session)
        if not resume:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Р РµР·СЋРјРµ РЅРµ РЅР°Р№РґРµРЅРѕ",
            )

        return await ResumeService.build_response(resume, session)

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get_all(
        user: User,
        filters: ResumeFilterQueryParams,
        session: AsyncSession,
    ) -> list[ResumeResponse]:
        
        if user.role == UserRole.CANDIDATE:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "РЈ РІР°СЃ РЅРµС‚ РїСЂР°РІ РїСЂРѕСЃРјР°С‚СЂРёРІР°С‚СЊ СЂРµР·СЋРјРµ",
            )
            
        resumes = list(await ResumeRepository.get_all(filters, session))

        if not resumes and filters.cursor:
            return []

        if not resumes:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Р РµР·СЋРјРµ РЅРµ РЅР°Р№РґРµРЅРѕ",
            )
        
        
        return [await ResumeService.build_response(item, session) for item in resumes]

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def search(
        user: User,
        resume_title: str,
        filters: ResumeFilterQueryParams,
        background: BackgroundTasks,
        session: AsyncSession,
    ) -> list[ResumeResponse]:
        
        if user.role == UserRole.CANDIDATE:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "РЈ РІР°СЃ РЅРµС‚ РїСЂР°РІ РїСЂРѕСЃРјР°С‚СЂРёРІР°С‚СЊ СЂРµР·СЋРјРµ",
            )
            
        resumes = list(await ResumeRepository.search(resume_title, filters, session))

        if not resumes and filters.cursor:
            return []

        if not resumes:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Р РµР·СЋРјРµ РЅРµ РЅР°Р№РґРµРЅРѕ",
            )

        background.add_task(SearchRequestService.create, user.uuid, resume_title)
        
        return [await ResumeService.build_response(item, session) for item in resumes]

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def create_education(
        user: User,
        resume_uuid: UUID,
        data: ResumeEducationCreateRequest,
        session: AsyncSession,
    ) -> ResumeEducation:
        
        if user.role == UserRole.COMPANY:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "РЈ РІР°СЃ РЅРµС‚ РїСЂР°РІ РёРјРµС‚СЊ СЂРµР·СЋРјРµ",
            )
            
        resume = await ResumeRepository.get(resume_uuid, session)
        
        if not resume:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Р РµР·СЋРјРµ РЅРµ РЅР°Р№РґРµРЅРѕ",
            )

        if resume.user_id != user.uuid:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "РЈ РІР°СЃ РЅРµС‚ РїСЂР°РІ РїСЂРѕСЃРјР°С‚СЂРёРІР°С‚СЊ СЌС‚Рѕ СЂРµР·СЋРјРµ",
            )

        education = ResumeEducation(resume_id=resume.uuid, **data.model_dump())
        
        return await ResumeRepository.create_education(education, session)

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def delete_education(
        user: User,
        resume_uuid: UUID,
        education_uuid: UUID,
        session: AsyncSession,
    ) -> ResumeEducation:
        
        if user.role == UserRole.COMPANY:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "РЈ РІР°СЃ РЅРµС‚ РїСЂР°РІ РёРјРµС‚СЊ СЂРµР·СЋРјРµ",
            )
            
        resume = await ResumeRepository.get(resume_uuid, session)
        
        if not resume:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Р РµР·СЋРјРµ РЅРµ РЅР°Р№РґРµРЅРѕ",
            )

        if resume.user_id != user.uuid:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "РЈ РІР°СЃ РЅРµС‚ РїСЂР°РІ РёР·РјРµРЅСЏС‚СЊ СЌС‚Рѕ СЂРµР·СЋРјРµ",
            )
            
        education = await ResumeRepository.get_education(education_uuid, session)

        if not education or education.resume_id != resume.uuid:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "РћР±СЂР°Р·РѕРІР°РЅРёРµ РЅРµ РЅР°Р№РґРµРЅРѕ",
            )

        return await ResumeRepository.delete_education(education, session)

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def create_experience(
        user: User,
        resume_uuid: UUID,
        data: ResumeExperienceCreateRequest,
        session: AsyncSession,
    ) -> ResumeExperience:
        
        if user.role == UserRole.COMPANY:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "РЈ РІР°СЃ РЅРµС‚ РїСЂР°РІ РёРјРµС‚СЊ СЂРµР·СЋРјРµ",
            )
            
        resume = await ResumeRepository.get(resume_uuid, session)
        
        if not resume:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Р РµР·СЋРјРµ РЅРµ РЅР°Р№РґРµРЅРѕ",
            )

        if resume.user_id != user.uuid:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "РЈ РІР°СЃ РЅРµС‚ РїСЂР°РІ РёР·РјРµРЅСЏС‚СЊ СЌС‚Рѕ СЂРµР·СЋРјРµ",
            )

        experience = ResumeExperience(resume_id=resume.uuid, **data.model_dump())
        
        return await ResumeRepository.create_experience(experience, session)

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def delete_experience(
        user: User,
        resume_uuid: UUID,
        experience_uuid: UUID,
        session: AsyncSession,
    ) -> ResumeExperience:
        
        if user.role == UserRole.COMPANY:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                "РЈ РІР°СЃ РЅРµС‚ РїСЂР°РІ РёРјРµС‚СЊ СЂРµР·СЋРјРµ",
            )
            
        resume = await ResumeRepository.get(resume_uuid, session)
        
        if not resume:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Р РµР·СЋРјРµ РЅРµ РЅР°Р№РґРµРЅРѕ",
            )

        if resume.user_id != user.uuid:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "РЈ РІР°СЃ РЅРµС‚ РїСЂР°РІ РёР·РјРµРЅСЏС‚СЊ СЌС‚Рѕ СЂРµР·СЋРјРµ",
            )
            
        experience = await ResumeRepository.get_experience(experience_uuid, session)

        if not experience or experience.resume_id != resume.uuid:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "РћРїС‹С‚ РЅРµ РЅР°РґРµРЅ",
            )

        return await ResumeRepository.delete_experience(experience, session)
    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def delete_resume(
        user: User,
        resume_uuid: UUID,
        session: AsyncSession,
    ) -> Resume:
        resume = await ResumeRepository.get(resume_uuid, session)

        if not resume:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                "Резюме не найдено",
            )

        if user.role != UserRole.ADMIN and resume.user_id != user.uuid:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                "У вас нет прав удалять это резюме",
            )

        return await ResumeRepository.delete(resume, session)

