from collections.abc import Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.ai.providers import OllamaProvider
from app.company.repository import CompanyRepository
from app.company.service import CompanyService
from app.enum import ResponseStatus, UserRole
from app.error_handler import handle_connection_errors, handle_model_errors
from app.response.model import Response
from app.response.repository import ResponseRepository
from app.response.schema import (
    AIResponseCreateRequest,
    AIResponseCreateResponse,
    ResponseCreateRequest,
)
from app.resume.services.resume import ResumeService
from app.users.model import User
from app.vacancy.filter import VacancyFilterQueryParams
from app.vacancy.services.vacancy import VacancyService

from .const import PROMPT
from .schema import ResponseUpdateStatusRequest


class ResponseService:
    @staticmethod
    def _format_experiences(experiences: list[dict[str, str]]) -> str:
        formatted: list[str] = []

        for item in experiences:
            company_name = item.get("company_name") or "Компания не указана"
            position = item.get("position") or "Должность не указана"
            description = item.get("description") or "Описание обязанностей не указано"
            formatted.append(
                f"Компания: {company_name}; Должность: {position}; Описание: {description}"
            )

        return "\n".join(formatted)

    @staticmethod
    def _sanitize_generated_text(text: str, candidate_name: str, company_name: str) -> str:
        cleaned = text.strip()

        replacements = {
            "[Company Name]": company_name,
            "[company]": company_name,
            "[Candidate's Name]": candidate_name,
            "[candidate]": candidate_name,
            "[candidate name]": candidate_name,
        }

        for placeholder, value in replacements.items():
            cleaned = cleaned.replace(placeholder, value or "")

        banned_fragments = [
            "опубликованной на вашем сайте",
            "размещенной на вашем сайте",
            "размещенной на сайте",
            "на вашем сайте",
        ]
        for fragment in banned_fragments:
            cleaned = cleaned.replace(fragment, "")

        cleaned = cleaned.replace("  ", " ")
        cleaned = cleaned.replace(" ,", ",")
        cleaned = cleaned.replace(" .", ".")

        return cleaned.strip()

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def generate(
        user: User,
        data: AIResponseCreateRequest,
        session: AsyncSession,
    ) -> AIResponseCreateResponse:
        if user.role != UserRole.CANDIDATE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только кандидат может создавать отклик",
            )

        resume = await ResumeService.get_my_resume(user, session)
        vacancy = await VacancyService.get(data.vacancy_uuid, session)
        company = await CompanyRepository.get(vacancy.company_id, session)

        if experiences := resume.experiences:
            experiences_payload = [
                {
                    "company_name": item.company_name or "",
                    "position": item.position or "",
                    "description": item.description or "",
                }
                for item in experiences
            ]
            experience = ResponseService._format_experiences(experiences_payload)
        else:
            experience = "Нет опыта"

        resume_parts = [resume.title or "", resume.about_me or ""]
        resume_summary = "\n".join(part for part in resume_parts if part) or "Информация о кандидате не указана"

        extra_context_parts: list[str] = []
        if data.tone:
            extra_context_parts.append(f"Тон письма: {data.tone}")
        if data.extra_context:
            extra_context_parts.append(data.extra_context.strip())
        extra_context = "\n".join(part for part in extra_context_parts if part).strip() or "Не указан"

        prompt = PROMPT.format(
            candidate_name=user.fio or "Кандидат",
            company_name=company.title if company else "",
            vacancy_title=vacancy.title,
            vacancy_description=vacancy.description or "",
            resume_summary=resume_summary,
            work_experience=experience,
            extra_context=extra_context,
        )

        provider = OllamaProvider(echo=False)
        text = await provider.chat(
            prompt=prompt,
            data={},
            timeout_seconds=15,
        )

        if not text:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="AI не вернул текст письма",
            )

        cleaned_text = ResponseService._sanitize_generated_text(
            text=text,
            candidate_name=user.fio or "Кандидат",
            company_name=company.title if company else "",
        )
        return AIResponseCreateResponse(text=cleaned_text)

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def create(
        user: User,
        data: ResponseCreateRequest,
        session: AsyncSession,
    ) -> Response:
        if user.role != UserRole.CANDIDATE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только кандидат может создавать отклик",
            )

        resume = await ResumeService.get_my_resume(user, session)
        vacancy = await VacancyService.get(data.vacancy_uuid, session)

        existing_response = await ResponseRepository.get_by_resume_and_vacancy(
            resume.uuid,
            vacancy.uuid,
            session,
        )

        if existing_response:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Отклик на эту вакансию с выбранным резюме уже существует",
            )

        response = Response(
            resume_id=resume.uuid,
            vacancy_id=vacancy.uuid,
            status=ResponseStatus.PENDING,
            message=data.message,
            employer_comment=None,
        )

        return await ResponseRepository.create(response, session)

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get_all(
        user: User,
        session: AsyncSession,
    ) -> Sequence[Response]:
        if user.role == UserRole.ADMIN:
            responses = await ResponseRepository.get_all(session)
        elif user.role == UserRole.CANDIDATE:
            responses = await ResponseRepository.get_by_candidate(user.uuid, session)
        else:
            company = await CompanyRepository.get_by_user(user.uuid, session)

            if not company:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Компания пользователя не найдена",
                )

            responses = await ResponseRepository.get_by_company(company.uuid, session)

        if not responses:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отклики не найдены",
            )

        return responses

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def get(
        user: User,
        response_uuid: UUID,
        session: AsyncSession,
    ) -> Response:
        response = await ResponseRepository.get(response_uuid, session)

        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отклик не найден",
            )

        if user.role == UserRole.CANDIDATE:
            resume = await ResumeService.get_my_resume(user, session)

            if not resume or resume.uuid != response.resume_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет доступа к этому отклику",
                )

        elif user.role == UserRole.COMPANY:
            user_company = await CompanyService.get_company(user, session)

            user_vacancies = await VacancyService.get_all(
                filters=VacancyFilterQueryParams(company_id=user_company["uuid"]),
                session=session,
            )

            response_vacancy = await VacancyService.get(response.vacancy_id, session)

            if response_vacancy not in user_vacancies:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет доступа к этому отклику",
                )

        return response

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def update_status(
        user: User,
        response_uuid: UUID,
        data: ResponseUpdateStatusRequest,
        session: AsyncSession,
    ) -> Response:
        if user.role == UserRole.CANDIDATE:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только работодатель может менять статус отклика",
            )

        response = await ResponseRepository.get(response_uuid, session)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отклик не найден",
            )

        if user.role == UserRole.COMPANY:
            user_company = await CompanyService.get_company(user, session)

            user_vacancies = await VacancyService.get_all(
                filters=VacancyFilterQueryParams(company_id=user_company["uuid"]),
                session=session,
            )

            response_vacancy = await VacancyService.get(response.vacancy_id, session)

            if response_vacancy not in user_vacancies:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Нет доступа к этому отклику",
                )

        response.status = data.status
        response.employer_comment = (data.employer_comment or "").strip() or None

        return await ResponseRepository.update(response, session)

    @staticmethod
    @handle_model_errors
    @handle_connection_errors
    async def delete(
        user: User,
        response_uuid: UUID,
        session: AsyncSession,
    ) -> Response:
        if user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Только администратор может удалять отклики",
            )

        response = await ResponseRepository.get(response_uuid, session)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отклик не найден",
            )

        return await ResponseRepository.delete(response, session)
