import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _build_database_url() -> str:
    """
    Builds a PostgreSQL database URL from environment variables with sensible defaults.

    This follows the platform instruction to use env vars if present, but also allows
    local/dev usage without having to configure anything.

    Expected env vars (from database container): POSTGRES_URL, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_PORT

    Notes:
    - In this multi-container setup, Postgres is expected to be reachable on port 5001.
    - Host defaults to 'localhost' for the preview environment.
    """
    # Full URL takes precedence if provided.
    postgres_url = os.getenv("POSTGRES_URL")
    if postgres_url:
        return postgres_url

    user = os.getenv("POSTGRES_USER", "appuser")
    password = os.getenv("POSTGRES_PASSWORD", "dbuser123")
    db = os.getenv("POSTGRES_DB", "myapp")
    port = os.getenv("POSTGRES_PORT", "5001")

    # If the platform injects a URL like postgresql://... we prefer that;
    # otherwise default to localhost to work in preview.
    host = os.getenv("POSTGRES_HOST", "localhost")

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db}"


DATABASE_URL = _build_database_url()

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# PUBLIC_INTERFACE
@contextmanager
def get_db_session():
    """Yield a SQLAlchemy session and ensure it is closed properly."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
