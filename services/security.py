# security.py
import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from uuid import UUID
from datetime import timedelta, timezone, datetime

from passlib.context import CryptContext

pw_context = CryptContext(schemes=["argon2"], deprecated="auto")

class TokenExpired(Exception):
    pass
class TokenInvalid(Exception):
    pass

def hash_password(password: str) -> str:
    return pw_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    return pw_context.verify(password, password_hash)

def create_access_token(*, user_id: UUID, secret_key: str, algo: str, ttl_minutes: int) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=ttl_minutes)

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    return jwt.encode(payload, secret_key, algorithm=algo)

def create_refresh_token(*, user_id: UUID, secret_key: str, algo: str, ttl_days: int) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(days=ttl_days)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, secret_key, algorithm=algo)

def decode_token(*, token: str, expected_type: str, secret_key: str, algo: str) -> UUID:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algo])
        if payload.get("type") != expected_type:
            raise TokenInvalid("Invalid token.")
        sub = payload.get("sub")
        if not sub:
            raise TokenInvalid("Invalid token: Missing sub claim")
        return UUID(sub)
    except ExpiredSignatureError as e:
        raise TokenExpired("Token has Expired") from e
    except InvalidTokenError as e:
        raise TokenInvalid("Invalid Token") from e