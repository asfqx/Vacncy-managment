from datetime import date
from uuid import UUID

from sqlalchemy import (
    ForeignKey,
    String,
    Text,
    Boolean,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base


class ResumeExperience(Base):

    resume_id: Mapped[UUID] = mapped_column(
        ForeignKey("resumes.uuid", ondelete="CASCADE"),
        index=True,
    )

    company_name: Mapped[str] = mapped_column(String(255))
    position: Mapped[str] = mapped_column(String(255))

    start_date: Mapped[date] = mapped_column()
    end_date: Mapped[date | None] = mapped_column(nullable=True)

    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
