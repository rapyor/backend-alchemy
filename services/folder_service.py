# services/folder_service.py
#
# Business logic for folders. This is where the RULES live:
#   - A user can only see/edit/delete THEIR OWN folders.
#   - Folder names can be updated.
#   - etc.
#
# The router doesn't enforce these rules — it just passes data here.
# The repository doesn't enforce them either — it just runs queries.
# The service is the brain in the middle.

from uuid import UUID
from models.folder import Folder
from repositories.folder_repository import FolderRepository


class FolderNotFound(Exception):
    """Raised when a folder doesn't exist or doesn't belong to the user."""
    pass


class FolderService:
    def __init__(self, folder_repo: FolderRepository):
        self.folder_repo = folder_repo

    def create_folder(self, *, name: str, user_id: UUID) -> Folder:
        """Create a new folder for the given user."""
        folder = self.folder_repo.create(name=name, user_id=user_id)
        # commit() saves to database, refresh() re-reads the row so we get
        # the database-generated values (id, created_at, updated_at).
        self.folder_repo.session.commit()
        self.folder_repo.session.refresh(folder)
        return folder

    def get_user_folders(self, *, user_id: UUID) -> list[Folder]:
        """Get all folders for a user. Returns empty list if they have none."""
        return self.folder_repo.get_all_by_user(user_id)

    def get_folder(self, *, folder_id: UUID, user_id: UUID) -> Folder:
        """Get a single folder, but ONLY if it belongs to this user.

        Why check user_id? Without it, any logged-in user could pass
        someone else's folder_id and access their folder. This is called
        an IDOR vulnerability (Insecure Direct Object Reference) — one of
        the most common security bugs in web apps.
        """
        folder = self.folder_repo.get_by_id(folder_id)
        if not folder or folder.user_id != user_id:
            # We say "not found" even if it exists but belongs to someone else.
            # Why? Saying "access denied" would confirm the folder EXISTS,
            # which leaks information. "Not found" reveals nothing.
            raise FolderNotFound("Folder not found.")
        return folder

    def update_folder(self, *, folder_id: UUID, user_id: UUID, name: str) -> Folder:
        """Rename a folder. Must belong to the requesting user."""
        folder = self.get_folder(folder_id=folder_id, user_id=user_id)
        # SQLAlchemy tracks changes to mapped objects automatically.
        # Just setting the attribute marks the row as "dirty" — commit()
        # will generate an UPDATE statement for only the changed columns.
        folder.name = name
        self.folder_repo.session.commit()
        self.folder_repo.session.refresh(folder)
        return folder

    def delete_folder(self, *, folder_id: UUID, user_id: UUID) -> None:
        """Delete a folder. Must belong to the requesting user."""
        folder = self.get_folder(folder_id=folder_id, user_id=user_id)
        self.folder_repo.delete(folder)
        self.folder_repo.session.commit()
