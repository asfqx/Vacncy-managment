from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text, DateTime, Integer, func, Enum
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Mapped, mapped_column

from app.enum import VacancyStatus
from app.core import Base


class Vacancy(Base):

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)

    company_id: Mapped[UUID] = mapped_column(ForeignKey("companys.uuid"))

    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    remote: Mapped[bool]

    salary: Mapped[int | None] = mapped_column(Integer, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(10), nullable=True)

    status: Mapped[VacancyStatus] = mapped_column(Enum(VacancyStatus), default=VacancyStatus.ACTIVE)

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
    