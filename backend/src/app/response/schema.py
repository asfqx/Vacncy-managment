from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.enum import ResponseStatus


class AIResponseCreateRequest(BaseModel):
    
    vacancy_uuid: UUID
    tone: str = Field(default="professional", max_length=50)
    extra_context: str | None = Field(default=None, max_length=2000)


class AIResponseCreateResponse(BaseModel):
    
    text: str


class ResponseCreateRequest(BaseModel):
    
    vacancy_uuid: UUID
    message: str = Field(min_length=20)


class ResponseUpdateStatusRequest(BaseModel):
    
    status: ResponseStatus
    employer_comment: str | None = Field(default=None, max_length=3000)


class ResponseResponse(BaseModel):
    
    uuid: UUID
    resume_id: UUID
    vacancy_id: UUID
    status: ResponseStatus
    message: str
    employer_comment: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }
