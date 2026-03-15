# security.py
#
# Pure utility functions for cryptography: password hashing and JWT tokens.
# This module has NO knowledge of the database, HTTP, or FastAPI.
# It only knows how to hash, verify, sign, and decode.

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError
from uuid import UUID
from datetime import timedelta, timezone, datetime

from passlib.context import CryptContext

# CryptContext manages password hashing. "schemes" tells it which algorithm to use.
# Argon2 is currently the strongest password hashing algorithm — it's designed to be
# slow and memory-intensive on purpose, making brute-force attacks impractical.
# "deprecated=auto" means: if we ever add a newer scheme, old hashes will be
# automatically re-hashed on the next successful login.
pw_context = CryptContext(schemes=["argon2"], deprecated="auto")


class TokenExpired(Exception):
    """Raised when a JWT's exp claim is in the past."""
    pass

class TokenInvalid(Exception):
    """Raised when a JWT signature is wrong or claims are missing."""
    pass


def hash_password(password: str) -> str:
    """One-way hash: "secret123" → "$argon2id$v=19$m=65536$..."
    You can never reverse this back to "secret123"."""
    return pw_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Hash the candidate password with the same salt and compare.
    Returns True if they match, False otherwise."""
    return pw_context.verify(password, password_hash)


def create_access_token(*, user_id: UUID, secret_key: str, algo: str, ttl_minutes: int) -> str:
    """Create a short-lived JWT for authenticating API requests.

    The payload contains:
      - sub: the user's UUID (who this token belongs to)
      - type: "access" (so we can distinguish from refresh tokens)
      - iat: issued-at timestamp
      - exp: expiration timestamp (after this, the token is rejected)

    The token is SIGNED with secret_key using the algo (HS256).
    This means anyone can READ the payload (it's just base64), but they
    can't MODIFY it without knowing the secret key — the signature would break.
    """
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=ttl_minutes)

    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }

    return jwt.encode(payload, secret_key, algorithm=algo)


# FIX: renamed parameter from ttl_days → ttl_minutes.
# The .env stores 1440 (minutes). The old code used timedelta(days=1440)
# which made tokens last ~4 years. Now both functions use minutes consistently.
def create_refresh_token(*, user_id: UUID, secret_key: str, algo: str, ttl_minutes: int) -> str:
    """Create a long-lived JWT used ONLY to obtain new access tokens.

    This token is signed with a DIFFERENT secret key than the access token.
    Why? If the access token key is ever compromised, the attacker still
    can't forge refresh tokens (and vice versa). Defense in depth.
    """
    now = datetime.now(timezone.utc)
    exp = now + timedelta(minutes=ttl_minutes)
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, secret_key, algorithm=algo)


def decode_token(*, token: str, expected_type: str, secret_key: str, algo: str) -> UUID:
    """Verify and decode a JWT. Returns the user UUID if valid.

    Steps:
    1. jwt.decode() checks the signature (was this signed with our key?)
       and checks expiration (is it still valid?). If either fails, it throws.
    2. We check the "type" claim matches what we expect (access vs refresh).
       This prevents someone from using a refresh token as an access token.
    3. We extract the "sub" claim (user UUID) and return it.
    """
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algo])

        # Prevent token type confusion: a refresh token should never
        # pass as an access token, even though both are valid JWTs.
        if payload.get("type") != expected_type:
            raise TokenInvalid("Invalid token type.")

        sub = payload.get("sub")
        if not sub:
            raise TokenInvalid("Invalid token: missing sub claim.")

        return UUID(sub)
    except ExpiredSignatureError as e:
        raise TokenExpired("Token has expired.") from e
    except InvalidTokenError as e:
        raise TokenInvalid("Invalid token.") from e
