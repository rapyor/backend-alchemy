from fastapi import Response

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"

COOKIE_SECURE = True
COOKIE_HTTPONLY = True
COOKIE_SAMESITE = "none"   # use "lax" if same-site frontend/backend
ACCESS_COOKIE_PATH = "/"
REFRESH_COOKIE_PATH = "/auth/refresh"

def set_auth_cookies(
    response: Response,
    *,
    access_token: str,
    refresh_token: str,
    access_max_age_seconds: int,
    refresh_max_age_seconds: int,
) -> None:
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=access_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path=ACCESS_COOKIE_PATH,
        max_age=access_max_age_seconds,
    )
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=COOKIE_HTTPONLY,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        path=REFRESH_COOKIE_PATH,
        max_age=refresh_max_age_seconds,
    )

def clear_auth_cookies(
    response: Response
) -> None:
    response.delete_cookie(
        key=ACCESS_COOKIE_NAME,
        path=ACCESS_COOKIE_PATH,
    )

    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path=REFRESH_COOKIE_PATH,
    )