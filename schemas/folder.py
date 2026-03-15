# schemas/folder.py
#
# Pydantic models for the folder endpoints.
# These are NOT database models — they define the shape of HTTP request/response JSON.
#
# Why separate from SQLAlchemy models?
#   - The database might store 10 columns, but the API only exposes 5.
#   - You don't want to accidentally leak password_hash in an API response.
#   - Request validation (min_length, max_length) belongs here, not in the DB model.
#   - The DB model represents "what's stored", schemas represent "what's sent/received."

from pydantic import BaseModel, Field
from datetime import datetime


class CreateFolderRequest(BaseModel):
    """What the client sends when creating a folder.
    Just a name — the user_id comes from the auth token, not the request body.
    Why? Because we never trust the client to tell us who they are.
    The token proves identity; the request body provides data."""
    name: str = Field(..., min_length=1, max_length=255)


class UpdateFolderRequest(BaseModel):
    """What the client sends when renaming a folder."""
    name: str = Field(..., min_length=1, max_length=255)


class FolderResponse(BaseModel):
    """What the API sends back — only the fields the client needs to see.
    Notice: user_id is included so the client knows who owns it,
    but password_hash or other sensitive fields never appear here."""
    id: str
    name: str
    user_id: str
    created_at: datetime
    updated_at: datetime
