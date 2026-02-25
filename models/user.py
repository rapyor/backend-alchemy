# models/user.py
import uuid
import datetime
from sqlalchemy import String, DateTime, func, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base

class User(Base):
   __tablename__ = "user" 

   id: Mapped[uuid.UUID] = mapped_column(
       UUID(as_uuid=True),
       primary_key=True,
       default=uuid.uuid4,
   )

   username: Mapped[str] = mapped_column(
       String(60),
       nullable=True,
       unique=True,
   )

   password_hash: Mapped[str | None] = mapped_column(
       String(320),
       nullable=True,
   )

   email: Mapped[str | None] = mapped_column(
       String(320),
       nullable=True,
       unique=True,
       index=True
   )

   is_active: Mapped[bool] = mapped_column(Boolean, default=True)

   created_at: Mapped[datetime.datetime] = mapped_column(
       DateTime,
       default=func.now()
   )
   updated_at: Mapped[datetime.datetime] = mapped_column(
       DateTime,
       default=func.now(),
       onupdate=func.now()
   )