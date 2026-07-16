"""
Database engine and session setup.

Reads DATABASE_URL from the environment, e.g.:
    postgresql+psycopg2://user:password@localhost:5432/monalearn

For local development without Postgres installed, DATABASE_URL can be left
unset and this falls back to a local SQLite file (monalearn.db) so the app
still runs — just don't expect production behavior from it (no real
concurrent writes, no array/ENUM types the way Postgres has them).
"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

load_dotenv()

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./monalearn.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: yields a session, closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Creates all tables if they don't exist yet.

    Fine for a prototype. The moment you need to change a table's shape on
    a database that already has real rows in it, replace this with Alembic
    migrations instead — create_all() only adds missing tables, it never
    alters existing ones.
    """
    from app import db_models  # noqa: F401  (import so models register on Base.metadata)
    Base.metadata.create_all(bind=engine)
