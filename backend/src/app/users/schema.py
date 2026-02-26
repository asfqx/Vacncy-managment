from pydantic import BaseModel, ConfigDict, EmailStr


class GetUserProfileResponse(BaseModel):

    email: EmailStr
    username: str
    avatar_url: str | None = None
    two_factor_enabled: bool

    model_config = ConfigDict(from_attributes=True)


class UpdateUserProfileRequest(BaseModel):

    username: str | None = None
    email: EmailStr | None = None
    avatar_url: str | None = None


class UpdateUserProfileResponse(GetUserProfileResponse): ...


class CreateQR2FAResponse(BaseModel):

    uri: str
    secret: str


class CreatePreSignedURLResponse(BaseModel):

    upload_url: str
