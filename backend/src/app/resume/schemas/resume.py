from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.enum import EducationLevel, Gender


class ResumeUpsertRequest(BaseModel):
    
    title: str = Field(min_length=2, max_length=255)
    about_me: str = Field(min_length=10)
    salary: int | None = Field(default=None, ge=0)
    currency: str | None = Field(default=None, max_length=10)
    gender: Gender | None = None
    birth_date: date | None = None


class ResumeEducationCreateRequest(BaseModel):
    
    institution: str = Field(min_length=2, max_length=255)
    level: EducationLevel
    specialization: str | None = Field(default=None, max_length=255)
    start_date: date | None = None
    end_date: date | None = None
    description: str | None = None
    is_current: bool = False


class ResumeExperienceCreateRequest(BaseModel):
    
    company_name: str = Field(min_length=2, max_length=255)
    position: str = Field(min_length=2, max_length=255)
    start_date: date
    end_date: date | None = None
    is_current: bool = False
    description: str | None = None


class ResumeEducationResponse(BaseModel):
    
    uuid: UUID
    resume_id: UUID
    institution: str
    level: EducationLevel
    specialization: str | None
    start_date: date | None
    end_date: date | None
    description: str | None
    is_current: bool

    model_config = {"from_attributes": True}


class ResumeExperienceResponse(BaseModel):
    
    uuid: UUID
    resume_id: UUID
    company_name: str
    position: str
    start_date: date
    end_date: date | None
    is_current: bool
    description: str | None

    model_config = {"from_attributes": True}


class ResumeResponse(BaseModel):
    
    uuid: UUID
    title: str
    about_me: str
    user_id: UUID
    salary: int | None
    currency: str | None
    gender: Gender | None
    birth_date: date | None
    created_at: datetime
    updated_at: datetime
    educations: list[ResumeEducationResponse]
    experiences: list[ResumeExperienceResponse]

    model_config = {"from_attributes": True}
