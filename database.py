from pathlib import Path
import sqlite3

# Emplacement de la base (dans le dossier du projet)
DB_PATH = Path(__file__).resolve().parent / "database.db"
DB_NAME = str(DB_PATH)  # utilisé par le reste du code

def _connect():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """Crée les tables si elles n'existent pas."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = _connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            nom  TEXT UNIQUE NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tutos (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            titre        TEXT NOT NULL,
            contenu      TEXT NOT NULL,
            categorie_id INTEGER NOT NULL,
            FOREIGN KEY (categorie_id) REFERENCES categories(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()

def peupler_exemples():
    """
    Ajoute quelques catégories et tutos de démonstration
    (uniquement si la base est vide).
    """
    init_db()
    conn = _connect()
    cur = conn.cursor()

    # Si aucune catégorie, on insère un jeu de base
    cur.execute("SELECT COUNT(*) FROM categories")
    if cur.fetchone()[0] == 0:
        categories = [
            "Survie en milieu naturel",
            "Nourriture & ressources",
            "Soins & premiers secours",
            "Énergie & technologie",
            "Bricolage & outils",
            "Communication locale",
        ]
        for nom in categories:
            cur.execute("INSERT OR IGNORE INTO categories(nom) VALUES (?)", (nom,))

        # Un ou deux tutos de démo
        cur.execute("SELECT id, nom FROM categories")
        cats = {nom: cid for cid, nom in cur.fetchall()}

        if "Soins & premiers secours" in cats:
            cid = cats["Soins & premiers secours"]
            cur.execute("INSERT INTO tutos(titre, contenu, categorie_id) VALUES (?,?,?)",
                        ("Désinfection", "Eau bouillie et alcool naturel.", cid))
            cur.execute("INSERT INTO tutos(titre, contenu, categorie_id) VALUES (?,?,?)",
                        ("Gérer une blessure", "Compression et élévation.", cid))

    conn.commit()
    conn.close()
