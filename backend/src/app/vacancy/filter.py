from typing import Annotated
from uuid import UUID
from datetime import datetime

from fastapi import Depends
from pydantic import BaseModel


class VacancyFilterQueryParams(BaseModel):

    remote: bool | None = None
    city: str | None = None
    salary_from: int | None = None
    salary_to: int | None = None
    include_archived: bool = False
    company_id: UUID | None = None
    
    cursor: datetime | None = None
    limit: int | None = None


VacancyFilterDepends = Annotated[VacancyFilterQueryParams, Depends()]
