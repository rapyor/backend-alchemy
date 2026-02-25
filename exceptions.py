
class AuthError(Exception):
    pass
class EmailAlreadyRegistered(AuthError):
    pass
class UsernameAlreadyTaken(AuthError):
    pass
class InvalidCredentials(AuthError):
    pass
class UserNotFound(AuthError):
    pass
class Unauthorized(AuthError):
    pass