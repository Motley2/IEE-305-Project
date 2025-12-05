from pathlib import Path
from sqlmodel import SQLModel, create_engine, Session, text

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "earthquakes.db"

# SQLite connection string with foreign key support
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Create engine with connection arguments for SQLite
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging
    connect_args={"check_same_thread": False}
)


def init_db():
    """
    Initialize the database by creating all tables.
    Call this once when setting up the database.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    SQLModel.metadata.create_all(engine)
    
    # Enable foreign keys for SQLite
    with Session(engine) as session:
        session.exec(text("PRAGMA foreign_keys = ON;"))
        session.commit()


def get_session():
    """
    Dependency function that yields a database session.
    Use with FastAPI's Depends() for automatic session management.
    """
    with Session(engine) as session:
        yield session