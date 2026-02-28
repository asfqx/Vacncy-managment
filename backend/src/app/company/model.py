from uuid import UUID

from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base


class Company(Base):
    
    user_uuid: Mapped[UUID] = mapped_column(
        ForeignKey(
            "users.uuid", 
            ondelete="CASCADE",
        ), 
        unique=True
    )

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String, default="") 
    website: Mapped[str] = mapped_column(String, default="") 
    company_size: Mapped[int] = mapped_column(Integer, default=0) 
    