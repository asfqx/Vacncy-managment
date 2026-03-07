from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from app.users.repository import UserRepository
from app.vacancy.models.vacancy import Vacancy
from app.vacancy.repositories.vacancy import VacancyRepository
from app.company.model import Company
from app.company.repository import CompanyRepository
from app.mock.data import MOCK_VACANCIES


async def insert_mock_vacancies(
    session: AsyncSession,
) -> None:
    
    user = await UserRepository.get_by_login("root", session)
    
    if not user:
        logger.info("Суперпользователь не создан")
        return
    
    company = await CompanyRepository.get_by_user(user.uuid, session)
    
    if not company:
        
        company = Company(
            user_uuid=user.uuid,
            title="Superuser company",
            description="Супермега крутая комапния",
            website="http://megapro.ru",
            company_size=100,
        )
        logger.info("Компания создана")
        
        await CompanyRepository.create(company, session)
        
    created_count = 0

    for data in MOCK_VACANCIES:
        request = Vacancy(
            title=data["title"],
            description=data["description"],
            company_id=company.uuid,
            city=data["city"],
            remote=data["remote"],
            salary=data["salary"],
            currency=data["currency"],
        )


        await VacancyRepository.create(request, session)
        created_count += 1


    logger.info(f"Создано вакансий: {created_count}")