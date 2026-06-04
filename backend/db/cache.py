import hashlib
import json
import sqlite3

DB_PATH = "fitfind_cache.db"


# --- Setup ---
# Called once at app startup. Creates the table if it doesn't exist yet.

def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS results_cache (
                key  TEXT PRIMARY KEY,
                data TEXT NOT NULL
            )
        """)


# --- Public interface ---

def make_key(query: str, sort: str, min_price: float, max_price: float) -> str:
    raw = f"{query}|{sort}|{min_price}|{max_price}"
    return hashlib.md5(raw.encode()).hexdigest()


def get_cached(key: str) -> list | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT data FROM results_cache WHERE key = ?", (key,)
        ).fetchone()
    return json.loads(row[0]) if row else None


def set_cached(key: str, results: list):
    with _connect() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO results_cache (key, data) VALUES (?, ?)",
            (key, json.dumps(results)),
        )


# --- Internal ---

def _connect() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)
