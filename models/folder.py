# models/folder.py
#
# This defines the "folder" table in the database.
# Each folder belongs to exactly ONE user (many-to-one relationship).
#
# In the database it looks like this:
#
#   user table                    folder table
#   ┌──────────┐                  ┌──────────────┐
#   │ id (PK)  │◄────────────────│ user_id (FK) │
#   │ username │                  │ id (PK)      │
#   │ ...      │                  │ name         │
#   └──────────┘                  │ created_at   │
#                                 │ updated_at   │
#                                 └──────────────┘
#
# PK = Primary Key (unique identifier for each row)
# FK = Foreign Key (a column that points to another table's PK)
#
# The FK is what creates the relationship. PostgreSQL will enforce it:
# you literally CANNOT insert a folder with a user_id that doesn't exist.

import uuid
import datetime
from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Folder(Base):
    __tablename__ = "folder"

    # Every folder gets its own unique UUID, just like users.
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # The folder's display name, e.g. "My Documents", "Photos".
    name: Mapped[str] = mapped_column(String(255))

    # FOREIGN KEY — this is the column that links a folder to its owner.
    # ForeignKey("user.id") means: this column references the "id" column
    # in the "user" table.
    #
    # ondelete="CASCADE" means: if the user is deleted, automatically delete
    # all their folders too. Without this, deleting a user would either fail
    # (because folders still reference them) or leave orphan rows.
    # nullable=False means: every folder MUST have an owner — no anonymous folders.
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )

    # RELATIONSHIP — this is NOT a database column. It's a Python-only
    # convenience that lets you do `folder.owner` to get the User object.
    # SQLAlchemy automatically runs the JOIN query for you behind the scenes.
    # back_populates="folders" connects this to User.folders (we'll add that next).
    owner: Mapped["User"] = relationship(back_populates="folders")

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )


# Why import User at the bottom?
# Python reads files top-to-bottom. If User imports Folder and Folder imports User,
# you get a circular import crash. Putting the import at the bottom (after the class
# is defined) avoids this. SQLAlchemy resolves the string "User" in the relationship
# lazily, so it works fine.
from models.user import User  # noqa: E402
