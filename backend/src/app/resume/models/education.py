from datetime import date
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    Enum,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base
from app.enum import EducationLevel


class ResumeEducation(Base):

    resume_id: Mapped[UUID] = mapped_column(
        ForeignKey("resumes.uuid", ondelete="CASCADE"),
        index=True,
    )

    institution: Mapped[str] = mapped_column(String(255))
    level: Mapped[EducationLevel] = mapped_column(
        Enum(EducationLevel, name="education_level_enum"),
        nullable=False,
    )

    specialization: Mapped[str | None] = mapped_column(String(255), nullable=True)

    start_date: Mapped[date | None] = mapped_column(nullable=True)
    end_date: Mapped[date | None] = mapped_column(nullable=True)

    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    