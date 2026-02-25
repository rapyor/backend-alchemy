# dependencies.py
from fastapi import Depends, HTTPException
from fastapi.security import APIKeyCookie
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from db.session import get_session
from sqlalchemy.orm import Session
from services.auth_service import AuthService
from repositories.user_repository import UserRepository

from schemas.auth import UserPublic
from services.auth_service import AuthService, Unauthorized, UserNotFound

# security = HTTPBearer()

# def get_auth_service(
#     session: Session = Depends(get_session)
# ) -> AuthService:
#     user_repo = UserRepository(session)
#     return AuthService(user_repo)

# def get_current_user(
#     creds: HTTPAuthorizationCredentials = Depends(security),
#     auth: AuthService = Depends(get_auth_service)
# ) -> UserPublic:

#     token = creds.credentials
#     try:
#         user = auth.get_user_by_token(
#             token=token
#         )
#         return UserPublic(
#             id=str(user.id),
#             username=user.username,
#             email=user.email,
#         )
#     except (Unauthorized, UserNotFound) as e:
#         raise HTTPException(status_code=401, detail=str(e))
        

access_cookie = APIKeyCookie(name="access_token", auto_error=False)
refresh_cookie = APIKeyCookie(name="refresh_token", auto_error=False)

def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    user_repo = UserRepository(session)
    return AuthService(user_repo)

def get_current_user(
    token: str | None = Depends(access_cookie),
    auth: AuthService = Depends(get_auth_service),
) -> UserPublic:
    if not token:
        raise HTTPException(status_code=401, detail="Missing access token")

    try:
        user = auth.get_user_by_token(token=token)
        return UserPublic(
            id=str(user.id),
            username=user.username,
            email=user.email,
        )
    except (Unauthorized, UserNotFound) as e:
        raise HTTPException(status_code=401, detail=str(e))

def get_refresh_token_from_cookie(
    token: str | None = Depends(refresh_cookie),
) -> str:
    if not token:
        raise HTTPException(status_code=401, detail="Missing refresh token")
    return token    