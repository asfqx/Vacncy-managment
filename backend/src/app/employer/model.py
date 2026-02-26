
from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base


class Employer(Base):
    
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "user.id", 
            ondelete="CASCADE",
        ), 
        unique=True
    )

    company_name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String, nullable=True, default="") 
    website: Mapped[str] = mapped_column(String, nullable=True, default="") 
    company_size: Mapped[int] = mapped_column(Integer, nullable=True, default=0) 
    