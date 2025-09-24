import sqlite3
from pathlib import Path
from argon2 import PasswordHasher
from argon2.low_level import Type

# ---- Chemin vers la base ----
DB_PATH = Path("storage/epsi_pedia.db")

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS utilisateurs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  nom_utilisateur TEXT NOT NULL UNIQUE,
  mot_de_passe_hachage TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin','user')),
  tentatives_echouees INTEGER NOT NULL DEFAULT 0,
  verrouille_jusqua INTEGER
);
"""

ph = PasswordHasher(
    time_cost=2,
    memory_cost=102400,
    parallelism=8,
    hash_len=32,
    salt_len=16,
    type=Type.ID
)

def init_db(admin_temp_password: str = "ChangeMe123!") -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        conn.executescript(SCHEMA_SQL)

        cur = conn.execute("SELECT 1 FROM utilisateurs WHERE nom_utilisateur = ?", ("admin",))
        if not cur.fetchone():
            pw_hash = ph.hash(admin_temp_password)
            conn.execute(
                """
                INSERT INTO utilisateurs (nom_utilisateur, mot_de_passe_hachage, role)
                VALUES (?, ?, 'admin')
                """,
                ("admin", pw_hash)
            )
            print("✔ Compte admin créé avec mot de passe temporaire.")
        else:
            print("ℹ Compte admin déjà présent.")

        conn.commit()

if __name__ == "__main__":
    init_db()
    print(f"✔ Base prête : {DB_PATH}")
