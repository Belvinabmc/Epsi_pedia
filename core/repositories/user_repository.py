# core/repositories/user_repository.py
import sqlite3, time
from typing import Optional, Dict
from core.config import DB_PATH, STORAGE_PATH
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    pw_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    lock_until INTEGER NOT NULL DEFAULT 0
);
"""

class UserRepository:
    def __init__(self, db_path: Path = DB_PATH):
        Path(STORAGE_PATH).mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        with sqlite3.connect(self.db_path) as con:
            con.execute(SCHEMA)
            con.commit()

    def get_by_username(self, username: str) -> Optional[Dict]:
        with sqlite3.connect(self.db_path) as con:
            con.row_factory = sqlite3.Row
            cur = con.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cur.fetchone()
            return dict(row) if row else None

    def create_user(self, username: str, pw_hash: str, role: str = "user"):
        with sqlite3.connect(self.db_path) as con:
            con.execute(
                "INSERT INTO users(username, pw_hash, role) VALUES(?,?,?)",
                (username, pw_hash, role)
            )
            con.commit()

    def update_attempts_and_lock(self, username: str, failed_attempts: int, lock_until: int):
        with sqlite3.connect(self.db_path) as con:
            con.execute(
                "UPDATE users SET failed_attempts=?, lock_until=? WHERE username=?",
                (failed_attempts, lock_until, username)
            )
            con.commit()

    def reset_attempts(self, username: str):
        self.update_attempts_and_lock(username, 0, 0)

    def update_password(self, username: str, new_hash: str):
        with sqlite3.connect(self.db_path) as con:
            con.execute("UPDATE users SET pw_hash=? WHERE username=?", (new_hash, username))
            con.commit()

    # util: bootstrap un admin par défaut si absent
    def ensure_default_admin(self, default_hash: str):
        if not self.get_by_username("admin"):
            self.create_user("admin", default_hash, role="admin")
