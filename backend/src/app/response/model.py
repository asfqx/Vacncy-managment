from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core import Base
from app.enum import ResponseStatus


class Response(Base):
    
    __table_args__ = (
        UniqueConstraint("resume_id", "vacancy_id", name="uq_responses_resume_vacancy"),
    )

    resume_id: Mapped[UUID] = mapped_column(
        ForeignKey("resumes.uuid", ondelete="CASCADE"),
        index=True,
    )
    vacancy_id: Mapped[UUID] = mapped_column(
        ForeignKey("vacancys.uuid", ondelete="CASCADE"),
        index=True,
    )

    status: Mapped[ResponseStatus] = mapped_column(
        Enum(ResponseStatus, name="response_status_enum"),
        default=ResponseStatus.PENDING,
    )
    message: Mapped[str] = mapped_column(Text)
    employer_comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
