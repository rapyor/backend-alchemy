# repositories/folder_repository.py
#
# Database operations for folders. Same pattern as UserRepository:
# the service tells us WHAT to do, we translate it into SQL via SQLAlchemy.

from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.folder import Folder


class FolderRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, *, name: str, user_id: UUID) -> Folder:
        """Insert a new folder row into the database."""
        folder = Folder(name=name, user_id=user_id)
        self.session.add(folder)
        # Remember: this just stages the insert. The service calls commit().
        return folder

    def get_by_id(self, folder_id: UUID) -> Folder | None:
        """Find a single folder by its ID. Returns None if not found."""
        return (
            self.session.execute(select(Folder).where(Folder.id == folder_id))
            .scalars()
            .first()
        )

    def get_all_by_user(self, user_id: UUID) -> list[Folder]:
        """Get ALL folders belonging to a specific user.

        This generates: SELECT * FROM folder WHERE user_id = ? ORDER BY created_at
        The ORDER BY makes the response predictable — oldest folders first.
        """
        return (
            self.session.execute(
                select(Folder)
                .where(Folder.user_id == user_id)
                .order_by(Folder.created_at)
            )
            .scalars()
            .all()
        )

    def delete(self, folder: Folder) -> None:
        """Remove a folder from the database.

        session.delete() stages the DELETE. Like add(), it's not permanent
        until commit() is called. This lets the service do multiple operations
        and commit them all at once (atomically — all succeed or all fail).
        """
        self.session.delete(folder)
