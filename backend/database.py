from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "database" / "earthquakes.db"
SCHEMA_PATH = BASE_DIR / "database" / "schema.sql"


def get_connection() -> sqlite3.Connection:
    """
    Return a SQLite connection. If the database file does not exist yet,
    this will create it and apply schema.sql.
    """
    first_time = not DB_PATH.exists()
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    if first_time:
        print("Initializing database from schema.sql ...")
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            sql_script = f.read()
        conn.executescript(sql_script)
        conn.commit()

    return conn