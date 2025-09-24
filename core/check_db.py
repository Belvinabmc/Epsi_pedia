import sqlite3
from pathlib import Path

DB_PATH = Path("storage/epsi_pedia.db")

def check_db():
    with sqlite3.connect(DB_PATH) as conn:
        c = conn.cursor()

        # Vérifier si la table existe
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='utilisateurs';")
        if c.fetchone():
            print("✔ Table 'utilisateurs' trouvée.")
        else:
            print("❌ Table 'utilisateurs' absente.")
            return

        # Afficher les utilisateurs existants
        c.execute("SELECT id, nom_utilisateur, role, tentatives_echouees, verrouille_jusqua FROM utilisateurs;")
        rows = c.fetchall()

        if rows:
            print("\nUtilisateurs trouvés :")
            for row in rows:
                print(row)
        else:
            print("\n⚠ Aucun utilisateur pour l'instant.")

if __name__ == "__main__":
    check_db()
