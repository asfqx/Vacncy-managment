from datetime import datetime, date
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, DateTime, Integer, func, Enum, Date
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base
from app.enum import Gender


class Resume(Base):

    title: Mapped[str] = mapped_column(String(255))
    about_me: Mapped[str] = mapped_column(Text)

    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.uuid", ondelete="CASCADE"),
        index=True,
    )

    salary: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)
    
    gender: Mapped[Gender | None] = mapped_column(
        Enum(Gender, name="gender_enum"),
        nullable=True,
    )
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    search_vector: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)
