# dependencies.py
#
# FastAPI's dependency injection system. These functions are called automatically
# when a route declares them with Depends(). They wire together the layers:
#   HTTP request → extract cookie → build service → return result
#
# This is the "glue" that connects routes to services without either knowing
# about the other's internals.

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyCookie
from sqlalchemy.orm import Session

from db.session import get_session
from repositories.user_repository import UserRepository
from repositories.folder_repository import FolderRepository
from schemas.auth import UserPublic
from services.auth_service import AuthService
from services.folder_service import FolderService
from exceptions import AuthError

# APIKeyCookie tells FastAPI: "look for a cookie with this name."
# auto_error=False means: don't throw automatically if missing — we handle it ourselves.
access_cookie = APIKeyCookie(name="access_token", auto_error=False)
refresh_cookie = APIKeyCookie(name="refresh_token", auto_error=False)


def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    """Build an AuthService for this request.

    FastAPI calls get_session() first (which opens a DB session),
    then passes it here. This is dependency injection — the route
    never has to know how to create a database session or repository.
    """
    user_repo = UserRepository(session)
    return AuthService(user_repo)


def get_current_user(
    token: str | None = Depends(access_cookie),
    auth: AuthService = Depends(get_auth_service),
) -> UserPublic:
    """Extract and validate the access token from the cookie, return the user.

    Any route that needs authentication just adds:
        user = Depends(get_current_user)
    and FastAPI handles the rest. If the token is missing or invalid,
    the user gets a 401 before the route function even runs.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Missing access token.")
    try:
        user = auth.get_user_by_token(token=token)
        return UserPublic(
            id=str(user.id),
            username=user.username,
            email=user.email,
        )
    # FIX: catch AuthError (base class) instead of importing specific subclasses.
    # This catches Unauthorized, UserNotFound, and any future auth exceptions.
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))


def get_refresh_token_from_cookie(
    token: str | None = Depends(refresh_cookie),
) -> str:
    """Extract the refresh token from the cookie. Just extraction, no validation.
    The actual validation happens in AuthService.refresh()."""
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token.")
    return token


def get_folder_service(session: Session = Depends(get_session)) -> FolderService:
    """Build a FolderService for this request. Same pattern as get_auth_service.

    Notice: both services get the SAME session type, but each request gets
    its own session instance (because get_session yields a new one each time).
    This means each request is its own database transaction.
    """
    folder_repo = FolderRepository(session)
    return FolderService(folder_repo)
