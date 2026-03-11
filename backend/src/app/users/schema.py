from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class CompanyProfileResponse(BaseModel):

    uuid: UUID
    title: str
    description: str
    website: str
    company_size: int

    model_config = ConfigDict(from_attributes=True)


class GetUserProfileResponse(BaseModel):

    uuid: UUID
    email: EmailStr
    username: str
    fio: str
    role: str
    status: str
    email_confirmed: bool
    avatar_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    last_login_at: datetime | None = None


class UpdateUserProfileRequest(BaseModel):

    username: str | None = None
    email: EmailStr | None = None
    fio: str | None = None
    avatar_url: str | None = None


class UpdateUserProfileResponse(BaseModel):

    username: str
    email: EmailStr
    fio: str
    avatar_url: str | None = None


class CreateQR2FAResponse(BaseModel):

    uri: str
    secret: str


class CreatePreSignedURLResponse(BaseModel):

    upload_url: str
