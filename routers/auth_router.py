# routers/auth_router.py
#
# This is the HTTP layer — it handles incoming requests and outgoing responses.
# Its job is thin: validate input (via Pydantic schemas), call the service,
# and translate service exceptions into HTTP status codes.
# It should contain NO business logic (that belongs in services/).

import os
from fastapi import HTTPException, APIRouter, Depends, Response
from dotenv import load_dotenv

from schemas.auth import (
    SignupRequest,
    LoginRequest,
    MeResponse,
    UserPublic,
)

from auth_cookies import set_auth_cookies, clear_auth_cookies

# FIX: import AuthError (the base class) so we can catch ALL auth exceptions
# in one place, instead of catching ValueError (which the service no longer raises).
from exceptions import (
    AuthError,
)
from services.auth_service import AuthService
from dependencies import get_auth_service, get_current_user, get_refresh_token_from_cookie

load_dotenv()
JWT_ACCESS_TTL_MINUTES = int(os.getenv("JWT_ACCESS_TTL_MINUTES"))
JWT_REFRESH_TTL_MINUTES = int(os.getenv("JWT_REFRESH_TTL_MINUTES"))

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/signup", response_model=MeResponse)
async def signup(
    payload: SignupRequest,
    auth: AuthService = Depends(get_auth_service)
):
    try:
        user = auth.signup(
            email=payload.email,
            username=payload.username,
            password=payload.password
        )
        # FIX: construct MeResponse correctly — it expects a `user` field
        # containing a UserPublic, not flat id/username/email fields.
        return MeResponse(
            user=UserPublic(
                id=str(user.id),
                username=user.username,
                email=user.email
            )
        )
    # FIX: the service raises AuthError subclasses (EmailAlreadyRegistered,
    # UsernameAlreadyTaken), not ValueError. The old code caught ValueError
    # but the exceptions inherited from AuthError — so they flew past the
    # except block and became unhandled 500 errors.
    except AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))


@auth_router.post("/login")
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

        # Cookie max_age is in seconds. Convert our minute-based config.
        access_max_age = JWT_ACCESS_TTL_MINUTES * 60

        # FIX: the old code did `JWT_REFRESH_TTL_MINUTES * 24 * 60 * 60`
        # which treated the value as DAYS and converted to seconds.
        # But the .env value is already in MINUTES (1440 min = 24 hours).
        # So we just multiply by 60 to get seconds.
        refresh_max_age = JWT_REFRESH_TTL_MINUTES * 60

        set_auth_cookies(
            response,
            access_token=token,
            refresh_token=refresh,
            access_max_age_seconds=access_max_age,
            refresh_max_age_seconds=refresh_max_age,
        )
        return {"detail": "Login successful"}
    # FIX: catch AuthError instead of ValueError, matching what the service throws.
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))


@auth_router.post("/refresh")
async def get_refresh_token(
    response: Response,
    token=Depends(get_refresh_token_from_cookie),
    auth: AuthService = Depends(get_auth_service)
):
    try:
        access_token, refresh = auth.refresh(refresh_token=token)

        access_max_age = JWT_ACCESS_TTL_MINUTES * 60
        # FIX: same TTL fix as login — minutes * 60 = seconds.
        refresh_max_age = JWT_REFRESH_TTL_MINUTES * 60

        set_auth_cookies(
            response,
            access_token=access_token,
            refresh_token=refresh,
            access_max_age_seconds=access_max_age,
            refresh_max_age_seconds=refresh_max_age,
        )
        return {"detail": "Token refreshed"}
    except AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))


@auth_router.get("/me", response_model=MeResponse)
async def me(user=Depends(get_current_user)):
    # `user` is already a UserPublic (built in dependencies.py).
    # We wrap it in MeResponse which adds the {"user": ...} envelope.
    return MeResponse(user=user)


@auth_router.post("/logout")
async def logout(response: Response):
    # Deleting the cookies is all we need — the tokens become inaccessible.
    # The tokens technically still "exist" and are valid until they expire,
    # but the browser no longer sends them. For true revocation you'd need
    # a server-side blocklist (a more advanced topic for later).
    clear_auth_cookies(response)
    return {"detail": "Logged out"}
