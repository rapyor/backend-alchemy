from uuid import UUID
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


from base import Base

class Subscription(Base):
    __tablename__ = "subscription"
    id: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

    billing_start: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=func.now()
    )
    billing_end: Mapped[datetime.datetime] = mapped_column(
        DateTime,
        default=func.now()
    )