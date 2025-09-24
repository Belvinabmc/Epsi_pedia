# database.py
import sqlite3

DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Table catégories
    cur.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT UNIQUE NOT NULL
    )
    """)

    # Table tutos
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tutos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        contenu TEXT NOT NULL,
        categorie_id INTEGER,
        FOREIGN KEY(categorie_id) REFERENCES categories(id)
    )
    """)

    conn.commit()
    conn.close()


def peupler_exemples():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    categories = [
        "🪵 Survie en milieu naturel",
        "🥫 Nourriture & ressources",
        "🩹 Soins & premiers secours",
        "🔋 Énergie & technologie",
        "🛠 Bricolage & outils",
        "📡 Communication locale"
    ]

    exemples = {
        "🪵 Survie en milieu naturel": [
            ("Faire du feu", "Apprendre à utiliser un silex ou une batterie pour allumer un feu."),
            ("Trouver de l’eau", "Utiliser la condensation et les plantes."),
            ("Construire un abri", "Avec des branches, feuilles, terre.")
        ],
        "🥫 Nourriture & ressources": [
            ("Conserver la viande", "Fumage et séchage naturel."),
            ("Techniques de pêche", "Utiliser un filet artisanal."),
            ("Plantes comestibles", "Identifier pissenlit, ortie, plantain.")
        ],
        "🩹 Soins & premiers secours": [
            ("Pansements maison", "Utiliser des tissus propres et du miel."),
            ("Gérer une blessure", "Compression et élévation."),
            ("Désinfection", "Eau bouillie et alcool naturel.")
        ],
        "🔋 Énergie & technologie": [
            ("Fabriquer une dynamo", "Avec un vélo et un alternateur."),
            ("Utiliser une batterie de voiture", "Pour alimenter une lampe."),
            ("Radio manuelle", "Construire une radio à galène.")
        ],
        "🛠 Bricolage & outils": [
            ("Fabriquer un couteau", "Avec pierre taillée et manche bois."),
            ("Réparer sans électricité", "Système de leviers et cordes."),
            ("Improviser des clous", "Utiliser du métal recyclé.")
        ],
        "📡 Communication locale": [
            ("Signaux de fumée", "Utiliser 3 colonnes pour urgence."),
            ("Code Morse", "Points et traits avec lampe."),
            ("Balises improvisées", "Pierres alignées en flèches.")
        ]
    }

    # Insérer catégories et tutos
    for cat in categories:
        cur.execute("INSERT OR IGNORE INTO categories (nom) VALUES (?)", (cat,))
        cur.execute("SELECT id FROM categories WHERE nom = ?", (cat,))
        cat_id = cur.fetchone()[0]

        for titre, contenu in exemples[cat]:
            cur.execute("""
            INSERT INTO tutos (titre, contenu, categorie_id)
            VALUES (?, ?, ?)
            """, (titre, contenu, cat_id))

    conn.commit()
    conn.close()
