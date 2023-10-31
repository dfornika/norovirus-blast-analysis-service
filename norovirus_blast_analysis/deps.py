from typing import Optional
from .database import SessionLocal


def get_db():
    """
    Get a database session.

    :return: A database session
    :rtype: SessionLocal
    """
    db: Optional[SessionLocal] = None
    try:
        db = SessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()
