# /services/auth_service.py
#
# This is the "business logic" layer for authentication.
# It sits between the router (HTTP layer) and the repository (database layer).
# The router should never touch the database directly — it asks this service.
# This service should never know about HTTP or cookies — it just returns data.

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
    EmailAlreadyRegistered,
    UsernameAlreadyTaken,
    UserNotFound,
    Unauthorized,
    InvalidCredentials,
)

# Load environment variables from .env file.
# NOTE: ideally load_dotenv() is called ONCE in app.py at startup,
# not in every file. We keep it here for now but this should be refactored.
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
        # Check if email/username already exist in the database.
        # We do this BEFORE creating the user to give a clear error message.
        user_by_email = self.user_repo.get_by_email(email) if email else None
        user_by_username = self.user_repo.get_by_username(username) if username else None

        # FIX: raise the specific exception for each case.
        # Previously both raised InvalidCredentials, which was misleading —
        # "invalid credentials" means wrong password, not "already taken."
        if user_by_email:
            raise EmailAlreadyRegistered("Email is already registered.")
        if user_by_username:
            raise UsernameAlreadyTaken("Username is already taken.")

        # Hash the password BEFORE storing. We never store plain text passwords.
        # Argon2 produces something like "$argon2id$v=19$m=65536$..." — a one-way
        # hash that can't be reversed back to the original password.
        pw_hash = hash_password(password)

        # Create the user row in the database.
        user = self.user_repo.create_user(
            username=username,
            password_hash=pw_hash,
            email=email
        )

        # commit() writes the pending changes to the database permanently.
        # refresh() re-reads the row so we get database-generated values
        # (like id, created_at) populated on our Python object.
        self.user_repo.session.commit()
        self.user_repo.session.refresh(user)
        return user

    def login(self, *, email: str | None, username: str | None, password: str) -> tuple[str, str]:
        # Look up the user by whatever identifier they provided.
        user_by_email = self.user_repo.get_by_email(email) if email else None
        user_by_username = self.user_repo.get_by_username(username) if username else None

        # If neither lookup found anyone, the user doesn't exist.
        if user_by_email is None and user_by_username is None:
            raise InvalidCredentials("Invalid credentials.")

        # Edge case: if they provided BOTH email and username, make sure
        # they point to the same account. Otherwise someone could log in
        # with one person's email and another person's username.
        if user_by_email and user_by_username and user_by_email.id != user_by_username.id:
            raise InvalidCredentials("Credentials do not match the same account.")

        # Pick whichever lookup succeeded.
        user = user_by_email or user_by_username
        if not user or not user.password_hash:
            raise InvalidCredentials("Invalid credentials.")

        # verify_password() hashes the provided password with the same algorithm
        # and compares it to the stored hash. This is how we check passwords
        # without ever storing or comparing plain text.
        if not verify_password(password, user.password_hash):
            raise InvalidCredentials("Invalid credentials.")

        # Authentication passed — mint JWT tokens.
        # Access token: short-lived, used for every API request.
        # Refresh token: long-lived, used ONLY to get a new access token.
        token = create_access_token(
            user_id=user.id,
            secret_key=JWT_SECRET_KEY,
            algo=JWT_ALGORITHM,
            ttl_minutes=JWT_ACCESS_TTL_MINUTES
        )
        # FIX: changed parameter name from ttl_days to ttl_minutes.
        # The .env value is 1440 minutes (= 24 hours). Previously this was
        # passed to ttl_days, which made the refresh token last ~4 YEARS.
        refresh_token = create_refresh_token(
            user_id=user.id,
            secret_key=JWT_REFRESH_KEY,
            algo=JWT_ALGORITHM,
            ttl_minutes=JWT_REFRESH_TTL_MINUTES
        )
        return token, refresh_token

    def get_user_by_token(self, *, token: str) -> User:
        """Given a JWT access token, return the User it belongs to."""
        try:
            # decode_token verifies the signature, checks expiration,
            # and extracts the user ID from the "sub" claim.
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

        # The token was valid, but the user might have been deleted since
        # the token was issued. Always verify the user still exists.
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFound("User not found.")
        return user

    def refresh(self, *, refresh_token: str) -> tuple[str, str]:
        """Use a refresh token to mint a fresh pair of access + refresh tokens."""
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

        # Mint a completely new pair. This is called "token rotation" —
        # every time you refresh, the old refresh token becomes useless
        # (once we add server-side revocation). This limits the damage
        # if a refresh token is ever stolen.
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
            ttl_minutes=JWT_REFRESH_TTL_MINUTES
        )
        return new_token, new_refresh
