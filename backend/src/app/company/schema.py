from uuid import UUID
from pydantic import BaseModel, Field


class CompanyCreateRequest(BaseModel):
    
    title: str = Field(min_length=2, max_length=255)
    description: str | None = Field(default=None, min_length=10)

    company_size: int | None = Field(default=None, ge=0)
    website: str | None = Field(default=None, max_length=255)
    

class CompanyUpdateRequest(BaseModel):
    
    title: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = Field(default=None, min_length=10)

    company_size: int | None = Field(default=None, ge=0)
    website: str | None = Field(default=None, max_length=255)


class CompanyResponse(BaseModel):
    
    uuid: UUID

    title: str 
    description: str 

    company_size: int 
    website: str 

    model_config = {
        "from_attributes": True,
    }
    