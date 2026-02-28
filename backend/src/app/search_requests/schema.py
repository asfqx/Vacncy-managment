from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class SearchRequestCreateRequest(BaseModel):
    
    request: str = Field(min_length=2, max_length=255)


class SearchRequestResponse(BaseModel):
    
    uuid: UUID

    user_uuid: UUID
    request: str
    
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }
    