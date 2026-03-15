# /repositories/user_repository.py
#
# The repository layer handles ALL direct database operations.
# It speaks SQLAlchemy, so the service layer doesn't have to.
# Think of it as a translator: the service says "get me user by email"
# and the repository translates that into the actual SQL query.

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.user import User


class UserRepository:
    def __init__(self, session: Session):
        # Each repository gets a database session injected.
        # The session is like a conversation with the database —
        # you queue up operations, then commit() sends them all at once.
        self.session = session

    def create_user(self, *, username: str | None, password_hash: str | None, email: str | None) -> User:
        # Create a Python object representing a new row.
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        # session.add() stages the insert — it's NOT in the database yet.
        # It will be written when the service calls session.commit().
        # We DON'T call session.refresh() here because the row doesn't exist
        # in the database yet — refresh() tries to re-read from the DB,
        # which would crash. The service handles commit + refresh.
        self.session.add(user)
        return user

    def get_by_id(self, user_id: UUID) -> User | None:
        # select(User).where(...) builds: SELECT * FROM "user" WHERE id = ?
        # .scalars() unwraps the result rows into User objects.
        # .first() returns the first match or None.
        return (
            self.session.execute(select(User).where(User.id == user_id))
            .scalars()
            .first()
        )

    def get_by_email(self, email: str) -> User | None:
        return (
            self.session.execute(select(User).where(User.email == email))
            .scalars()
            .first()
        )

    def get_by_username(self, username: str) -> User | None:
        return (
            self.session.execute(select(User).where(User.username == username))
            .scalars()
            .first()
        )
