from datetime import date

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from app.company.model import Company
from app.company.repository import CompanyRepository
from app.enum import UserRole
from app.mock.data import CANDIDATE_PASSWORD, EMPLOYER_PASSWORD, MOCK_CANDIDATES, MOCK_EMPLOYERS
from app.resume.models.education import ResumeEducation
from app.resume.models.expirience import ResumeExperience
from app.resume.models.resume import Resume
from app.resume.repository import ResumeRepository
from app.security import Argon2Hasher
from app.users.model import User
from app.users.repository import UserRepository
from app.vacancy.filter import VacancyFilterQueryParams
from app.vacancy.model import Vacancy
from app.vacancy.repository import VacancyRepository


async def _get_or_create_user(
    session: AsyncSession,
    *,
    email: str,
    username: str,
    fio: str,
    role: UserRole,
    password: str,
) -> tuple[User, bool]:
    existing_user = await UserRepository.get_by_login(username, session)
    if existing_user:
        return existing_user, False

    user = User(
        email=email.lower(),
        username=username,
        fio=fio,
        role=role,
        password_hash=Argon2Hasher.hash(password),
        email_confirmed=True,
    )
    user = await UserRepository.create(user, session)
    return user, True


async def insert_mock_vacancies(
    session: AsyncSession,
) -> None:
    created_employers = 0
    created_companies = 0
    created_vacancies = 0
    created_candidates = 0
    created_resumes = 0

    for profile in MOCK_EMPLOYERS:
        user, user_created = await _get_or_create_user(
            session,
            email=profile["user"]["email"],
            username=profile["user"]["username"],
            fio=profile["user"]["fio"],
            role=UserRole.COMPANY,
            password=EMPLOYER_PASSWORD,
        )
        if user_created:
            created_employers += 1

        company = await CompanyRepository.get_by_user(user.uuid, session)
        if not company:
            company = Company(
                user_uuid=user.uuid,
                title=profile["company"]["title"],
                description=profile["company"]["description"],
                website=profile["company"]["website"],
                company_size=profile["company"]["company_size"],
            )
            company = await CompanyRepository.create(company, session)
            created_companies += 1

        existing_vacancies = await VacancyRepository.get_all(
            VacancyFilterQueryParams(company_id=company.uuid, include_archived=True, limit=2),
            session,
        )
        if not existing_vacancies:
            for vacancy_data in profile["vacancies"]:
                vacancy = Vacancy(
                    title=vacancy_data["title"],
                    description=vacancy_data["description"],
                    company_id=company.uuid,
                    city=vacancy_data["city"],
                    remote=vacancy_data["remote"],
                    salary=vacancy_data["salary"],
                    currency=vacancy_data["currency"],
                )
                created = await VacancyRepository.create(vacancy, session)
                if created:
                    created_vacancies += 1

    for profile in MOCK_CANDIDATES:
        user, user_created = await _get_or_create_user(
            session,
            email=profile["user"]["email"],
            username=profile["user"]["username"],
            fio=profile["user"]["fio"],
            role=UserRole.CANDIDATE,
            password=CANDIDATE_PASSWORD,
        )
        if user_created:
            created_candidates += 1

        existing_resume = await ResumeRepository.get_by_user(user.uuid, session)
        if existing_resume:
            continue

        resume = Resume(
            user_id=user.uuid,
            title=profile["resume"]["title"],
            about_me=profile["resume"]["about_me"],
            salary=profile["resume"]["salary"],
            currency=profile["resume"]["currency"],
            gender=profile["resume"]["gender"],
            birth_date=date.fromisoformat(profile["resume"]["birth_date"]),
        )
        resume = await ResumeRepository.create(resume, session)
        created_resumes += 1

        for education_data in profile["educations"]:
            await ResumeRepository.create_education(
                ResumeEducation(
                    resume_id=resume.uuid,
                    institution=education_data["institution"],
                    level=education_data["level"],
                    specialization=education_data["specialization"],
                    start_date=date.fromisoformat(education_data["start_date"]) if education_data["start_date"] else None,
                    end_date=date.fromisoformat(education_data["end_date"]) if education_data["end_date"] else None,
                    description=education_data["description"],
                    is_current=education_data["is_current"],
                ),
                session,
            )

        for experience_data in profile["experiences"]:
            await ResumeRepository.create_experience(
                ResumeExperience(
                    resume_id=resume.uuid,
                    company_name=experience_data["company_name"],
                    position=experience_data["position"],
                    start_date=date.fromisoformat(experience_data["start_date"]),
                    end_date=date.fromisoformat(experience_data["end_date"]) if experience_data["end_date"] else None,
                    description=experience_data["description"],
                    is_current=experience_data["is_current"],
                ),
                session,
            )

    logger.info(
        "Моки обновлены: создано работодателей={}, компаний={}, вакансий={}, кандидатов={}, резюме={}",
        created_employers,
        created_companies,
        created_vacancies,
        created_candidates,
        created_resumes,
    )
