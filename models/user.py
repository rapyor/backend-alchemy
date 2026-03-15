# models/user.py
import uuid
import datetime
from sqlalchemy import String, DateTime, func, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

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

   # RELATIONSHIP — the reverse side of Folder.owner.
   # This is NOT a column in the database. It's a Python convenience.
   # It lets you do: user.folders → [Folder(...), Folder(...), ...]
   #
   # back_populates="owner" connects this to Folder.owner, so if you
   # set folder.owner = some_user, that folder automatically appears
   # in some_user.folders too. They stay in sync.
   #
   # cascade="all, delete-orphan" means:
   #   - If you delete a user, SQLAlchemy deletes their folders too
   #   - If you remove a folder from user.folders, it gets deleted
   #     (not just unlinked — "orphan" folders aren't allowed)
   folders: Mapped[list["Folder"]] = relationship(
       back_populates="owner",
       cascade="all, delete-orphan",
   )