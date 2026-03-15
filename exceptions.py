# exceptions.py
#
# Custom exception hierarchy for the auth system.
#
# Why not just use ValueError everywhere? Because:
# 1. Specific exceptions let the router return the RIGHT HTTP status code.
#    EmailAlreadyRegistered → 400, InvalidCredentials → 401, etc.
# 2. They all inherit from AuthError, so you can catch the whole family
#    with `except AuthError` when you don't need to distinguish.
# 3. They make debugging easier — seeing "EmailAlreadyRegistered" in a
#    traceback is way more helpful than seeing "ValueError".


class AuthError(Exception):
    """Base class for all authentication/authorization errors."""
    pass

class EmailAlreadyRegistered(AuthError):
    """Signup attempted with an email that already has an account."""
    pass

class UsernameAlreadyTaken(AuthError):
    """Signup attempted with a username that already exists."""
    pass

class InvalidCredentials(AuthError):
    """Login failed — wrong email/username/password combination."""
    pass

class UserNotFound(AuthError):
    """Token was valid but the user no longer exists in the database."""
    pass

class Unauthorized(AuthError):
    """Token is expired, malformed, or otherwise invalid."""
    pass
