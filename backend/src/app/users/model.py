from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base

from .enum import UserRole


class User(Base):
    
    email: Mapped[str] = mapped_column(String(255), unique=True)
    
    username: Mapped[str] = mapped_column(String(100))
    
    fio: Mapped[str] = mapped_column(String(50))
    
    role: Mapped[UserRole]
    
    password_hash: Mapped[str] = mapped_column(String(255))
    
    email_confirmed: Mapped[bool] = mapped_column(default=False)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
