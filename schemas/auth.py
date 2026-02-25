# /schemas/auth.py
from uuid import UUID

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, model_validator
from typing_extensions import Self

class SignupRequest(BaseModel):
    username: str | None = Field(..., min_length=4, max_length=64)
    email: EmailStr | None = None
    password: str = Field(..., min_length=8, max_length=128)

    @model_validator(mode="after")
    def either_email_or_username(self) -> Self:
        if not self.username and not self.email:
            raise ValueError("Provider at least email or username")
        return self
    
class LoginRequest(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    password: str = Field(..., min_length=8, max_length=128)
    
    @model_validator(mode="after")
    def either_email_or_username(self) -> Self:
        if not self.username and not self.email:
            raise ValueError("Provider at least email or username")
        return self

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class UserPublic(BaseModel):
    id: str
    username: str | None = None
    email: EmailStr | None = None

class MeResponse(BaseModel):
    user: UserPublic

class LoginResponse(BaseModel):
    access_token: str
    access_type: str = "bearer"