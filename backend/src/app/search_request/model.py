from uuid import UUID
from datetime import datetime

from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base


class SearchRequest(Base):
    
    user_uuid: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.uuid", 
            ondelete="CASCADE",
        ), 
    )
    
    request: Mapped[str]
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    