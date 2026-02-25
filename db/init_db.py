# db/init_db.py
from db.session import engine
from models.base import Base

from models.user import User


def init_db() -> None:
    Base.metadata.create_all(engine)
    
if __name__ == "__main__":
    init_db()
    print("Table created")