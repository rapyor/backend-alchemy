# routers/auth_router.py
import os
from fastapi import HTTPException, APIRouter, Depends, Request, Response
from fastapi.security import HTTPAuthorizationCredentials,  HTTPBearer
from dotenv import load_dotenv


from schemas.auth import (
    SignupRequest,
    LoginRequest,
    TokenResponse,
    MeResponse
)

from auth_cookies import set_auth_cookies, clear_auth_cookies

from exceptions import (
    Unauthorized,
    UserNotFound
)
from services.auth_service import AuthService
from dependencies import get_auth_service, get_current_user, get_refresh_token_from_cookie

load_dotenv()
JWT_ACCESS_TTL_MINUTES = int(os.getenv("JWT_ACCESS_TTL_MINUTES"))
JWT_REFRESH_TTL_MINUTES = int(os.getenv("JWT_REFRESH_TTL_MINUTES"))

# access_bearer = HTTPBearer()
# refresh_bearer = HTTPBearer()

auth_router = APIRouter(prefix="/auth", tags=["Auth"])

# WE MUST THINK OF DB ASYNC IF THE SERVER IS ASYNC; REFACTOR LATER
@auth_router.post(
    "/signup",
    response_model=MeResponse
)
async def signup(
    payload: SignupRequest,
    auth: AuthService = Depends(get_auth_service)
):
    try: 
        user = auth.register(
            email=payload.email,
            username=payload.username,
            password=payload.password
        )
        return MeResponse(
            id=str(user.id),
            username=user.username,
            email=user.email
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@auth_router.post(
    "/login"
)
async def login(
    payload: LoginRequest,
    response: Response,
    auth: AuthService = Depends(get_auth_service),
):
    try:
        token, refresh = auth.login(
            username=payload.username,
            email=payload.email,
            password=payload.password
        )
        # convert your TTL config values to seconds (adapt names to your actual config)
        access_max_age = int(JWT_ACCESS_TTL_MINUTES * 60)
        # NOTE: if your refresh config is actually "days", convert correctly
        refresh_max_age = int(JWT_REFRESH_TTL_MINUTES * 24 * 60 * 60)

        set_auth_cookies(
            response,
            access_token=token,
            refresh_token=refresh,
            access_max_age_seconds=access_max_age,
            refresh_max_age_seconds=refresh_max_age,
        )
        return {"detail": "Login successful"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@auth_router.post(
    "/refresh"
)
async def get_refresh_token(
    response: Response,
    token = Depends(get_refresh_token_from_cookie),
    auth: AuthService = Depends(get_auth_service)
):
    try:
        access_token, refresh = auth.refresh(
            refresh_token=token
        )
        access_max_age = int(JWT_ACCESS_TTL_MINUTES * 60)
        refresh_max_age = int(JWT_REFRESH_TTL_MINUTES * 24 * 60 * 60)

        set_auth_cookies(
            response,
            access_token=access_token,
            refresh_token=refresh,
            access_max_age_seconds=access_max_age,
            refresh_max_age_seconds=refresh_max_age,
        )
        return {"detail": "Token refreshed"}
    except (Unauthorized, UserNotFound) as e:
        raise HTTPException(status_code=401, detail=str(e))

@auth_router.get(
    "/me",
    response_model=MeResponse
)
async def me( user = Depends(get_current_user) ):
    return MeResponse(user=user)

@auth_router.post("/logout")
async def logout(response: Response):
    clear_auth_cookies(response)
    return {"detail": "Logged out"}
