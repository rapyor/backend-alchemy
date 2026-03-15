# routers/folder_router.py
#
# HTTP endpoints for folder CRUD (Create, Read, Update, Delete).
# Every endpoint requires authentication — the user must be logged in.
#
# REST convention for URL design:
#   POST   /folders          → create a new folder
#   GET    /folders          → list all your folders
#   GET    /folders/{id}     → get one specific folder
#   PUT    /folders/{id}     → update a folder
#   DELETE /folders/{id}     → delete a folder
#
# Notice the pattern: the noun is plural ("/folders"), the HTTP method
# is the verb (POST=create, GET=read, PUT=update, DELETE=delete).

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException

from schemas.folder import CreateFolderRequest, UpdateFolderRequest, FolderResponse
from schemas.auth import UserPublic
from services.folder_service import FolderService, FolderNotFound
from dependencies import get_current_user, get_folder_service

folder_router = APIRouter(prefix="/folders", tags=["Folders"])


def _folder_to_response(folder) -> FolderResponse:
    """Convert a SQLAlchemy Folder object to a Pydantic response.
    This helper avoids repeating the same conversion in every endpoint."""
    return FolderResponse(
        id=str(folder.id),
        name=folder.name,
        user_id=str(folder.user_id),
        created_at=folder.created_at,
        updated_at=folder.updated_at,
    )


@folder_router.post("", response_model=FolderResponse, status_code=201)
async def create_folder(
    payload: CreateFolderRequest,
    user: UserPublic = Depends(get_current_user),
    service: FolderService = Depends(get_folder_service),
):
    """Create a new folder for the authenticated user.

    Notice: user_id comes from the JWT token (via get_current_user),
    NOT from the request body. The client never tells us who they are —
    the token proves it. This prevents users from creating folders
    under someone else's account.

    status_code=201: HTTP convention — 201 means "created successfully"
    (as opposed to 200 which just means "OK").
    """
    folder = service.create_folder(
        name=payload.name,
        user_id=UUID(user.id),
    )
    return _folder_to_response(folder)


@folder_router.get("", response_model=list[FolderResponse])
async def list_folders(
    user: UserPublic = Depends(get_current_user),
    service: FolderService = Depends(get_folder_service),
):
    """List ALL folders for the authenticated user.
    Returns an empty list if they have no folders — not a 404."""
    folders = service.get_user_folders(user_id=UUID(user.id))
    return [_folder_to_response(f) for f in folders]


@folder_router.get("/{folder_id}", response_model=FolderResponse)
async def get_folder(
    folder_id: UUID,
    user: UserPublic = Depends(get_current_user),
    service: FolderService = Depends(get_folder_service),
):
    """Get a single folder by ID.

    folder_id is a PATH PARAMETER — it comes from the URL itself:
    GET /folders/550e8400-e29b-41d4-a716-446655440000
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ this part

    FastAPI automatically parses it into a UUID and returns 422
    if the client sends something that isn't a valid UUID.
    """
    try:
        folder = service.get_folder(folder_id=folder_id, user_id=UUID(user.id))
        return _folder_to_response(folder)
    except FolderNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@folder_router.put("/{folder_id}", response_model=FolderResponse)
async def update_folder(
    folder_id: UUID,
    payload: UpdateFolderRequest,
    user: UserPublic = Depends(get_current_user),
    service: FolderService = Depends(get_folder_service),
):
    """Rename a folder. Only the owner can do this."""
    try:
        folder = service.update_folder(
            folder_id=folder_id,
            user_id=UUID(user.id),
            name=payload.name,
        )
        return _folder_to_response(folder)
    except FolderNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@folder_router.delete("/{folder_id}", status_code=204)
async def delete_folder(
    folder_id: UUID,
    user: UserPublic = Depends(get_current_user),
    service: FolderService = Depends(get_folder_service),
):
    """Delete a folder. Only the owner can do this.

    status_code=204: HTTP convention — "No Content". Means "done, nothing to return."
    The response body is empty, which makes sense — the thing is gone.
    """
    try:
        service.delete_folder(folder_id=folder_id, user_id=UUID(user.id))
    except FolderNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
