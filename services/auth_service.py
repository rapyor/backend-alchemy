# /services/auth_service.py
import os
from dotenv import load_dotenv
from models.user import User
from repositories.user_repository import UserRepository

from services.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    TokenExpired,
    TokenInvalid,
)

from exceptions import (
    AuthError,
    EmailAlreadyRegistered,
    UsernameAlreadyTaken,
    UserNotFound,
    Unauthorized,
    InvalidCredentials,
)
load_dotenv()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_REFRESH_KEY = os.getenv("JWT_REFRESH_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
JWT_ACCESS_TTL_MINUTES = int(os.getenv("JWT_ACCESS_TTL_MINUTES"))
JWT_REFRESH_TTL_MINUTES = int(os.getenv("JWT_REFRESH_TTL_MINUTES"))

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def signup(self, *, email: str | None, username: str | None, password: str) -> User:
        user_by_email = self.user_repo.get_by_email(email) if email else None
        user_by_username = self.user_repo.get_by_username(username) if username else None

        if user_by_email:
            raise InvalidCredentials("Invalid credentials")
        if user_by_username:
            raise InvalidCredentials("Invalid credentials.")
        
        pw_hash = hash_password(password)
        user = self.user_repo.create_user(
            username=user_by_username,
            password_hash=pw_hash,
            email=user_by_email
        )
        self.user_repo.session.commit()
        self.user_repo.session.refresh(user)
        return user
    
    def login(self, *, email: str | None, username: str | None, password: str) -> tuple[str, str]:
        user_by_email = self.user_repo.get_by_email(email) if email else None
        user_by_username = self.user_repo.get_by_username(username) if username else None

        if user_by_email is None and user_by_username is None:
            raise ValueError("Invalid credentials.")
        
        if user_by_email and user_by_username and user_by_email.id != user_by_username.id:
            raise ValueError("Credential do not match same account!")
        
        user = user_by_email or user_by_username
        if not user or not user.password_hash:
            raise ValueError("Invalid credentials.")
        
        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials.")
        
        # after check: we mint the access token
        token = create_access_token(
            user_id=user.id,
            secret_key=JWT_SECRET_KEY,
            algo=JWT_ALGORITHM,
            ttl_minutes=JWT_ACCESS_TTL_MINUTES
        )

        refresh_token = create_refresh_token(
            user_id=user.id,
            secret_key=JWT_REFRESH_KEY,
            algo=JWT_ALGORITHM,
            ttl_days=JWT_REFRESH_TTL_MINUTES
        )

        return token, refresh_token
    
    def get_user_by_token(self, *, token: str) -> User:
        try:
            user_id = decode_token(
                token=token,
                expected_type="access",
                secret_key=JWT_SECRET_KEY,
                algo=JWT_ALGORITHM
            )
        except TokenExpired as e:
            raise Unauthorized(str(e)) from e
        except TokenInvalid as e:
            raise Unauthorized(str(e)) from e

        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("User not Found")
        return user
    
    def refresh(self, *, refresh_token: str) -> tuple[str, str]:
        try:
            user_id = decode_token(
                token=refresh_token,
                expected_type="refresh",
                secret_key=JWT_REFRESH_KEY,
                algo=JWT_ALGORITHM
            )
        except (TokenExpired, TokenInvalid) as e:
            raise Unauthorized(str(e)) from e
        
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("User not found.")

        new_token = create_access_token(
            user_id=user.id,
            secret_key=JWT_SECRET_KEY,
            algo=JWT_ALGORITHM,
            ttl_minutes=JWT_ACCESS_TTL_MINUTES
        )
        new_refresh = create_refresh_token(
            user_id=user.id,
            secret_key=JWT_REFRESH_KEY,
            algo=JWT_ALGORITHM,
            ttl_days=JWT_REFRESH_TTL_MINUTES
        )

        return new_token, new_refresh

    