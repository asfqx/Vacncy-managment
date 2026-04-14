from typing import Annotated
from datetime import datetime, date
from uuid import UUID

from fastapi import Depends
from pydantic import BaseModel

from app.enum import Gender, EducationLevel


class ResumeFilterQueryParams(BaseModel):
    gender: Gender | None = None
    education_level: EducationLevel | None = None
    salary_from: int | None = None
    salary_to: int | None = None
    birth_date_from: date | None = None
    birth_date_to: date | None = None
    cursor: datetime | None = None
    cursor_uuid: UUID | None = None
    limit: int | None = None


ResumeFilterDepends = Annotated[ResumeFilterQueryParams, Depends()]
