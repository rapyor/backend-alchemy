import uuid
from datetime import datetime
from typing import Literal
from sqlalchemy import UUID, String, DateTime, Boolean, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base

Provider = Literal["google"]

class UserIdentity(Base):
    __tablename__ = "user_identity"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    provider_subject: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=func.now()
    )

    # updated_at: Mapped[datetime.datetime] = mapped_column(
    #     DateTime,
    #     default=func.now(),
    #     onupdate=func.now(),
    # )

    # NEED TO DO RESEARCH ON THIS
    __table_args__ = (
        UniqueConstraint("provider", "provider_subject", name="uq_provider_subject"),
    )
        
    
    