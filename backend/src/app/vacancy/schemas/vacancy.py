from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from app.enum import VacancyStatus


class VacancyCreateRequest(BaseModel):
    
    title: str = Field(min_length=2, max_length=255)
    description: str = Field(min_length=10)

    city: str | None = Field(default=None, max_length=120)
    remote: bool = False

    salary: int | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, max_length=10)
    

class VacancyUpdateRequest(BaseModel):
    
    title: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = Field(default=None, min_length=10)

    city: str | None = Field(default=None, max_length=120)
    remote: bool | None = None

    salary: int | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, max_length=10)


class VacancyResponse(BaseModel):
    
    uuid: UUID

    title: str
    description: str

    company_id: UUID

    city: str | None
    remote: bool

    salary: int | None
    currency: str | None

    status: VacancyStatus

    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
    