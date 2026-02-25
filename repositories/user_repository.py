# /repositories/user_repository.py
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.user import User

class UserRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def create_user(self, *, username: str | None, password_hash: str | None, email: str | None) -> User:
        user = User(
            username=username,
            email=email,
            password_hash=password_hash
        )
        self.session.add(user)
        self.session.refresh(user)
        return user
    
    def get_by_id(self, user_id: UUID) -> User | None:
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