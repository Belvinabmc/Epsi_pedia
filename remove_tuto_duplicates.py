import sqlite3

DB_NAME = "database1.db"

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# Supprime tous les doublons, ne garde que le tuto avec l'id le plus bas pour chaque titre
cur.execute('''
DELETE FROM tutos
WHERE id NOT IN (
    SELECT MIN(id)
    FROM tutos
    GROUP BY titre
)
''')
conn.commit()
conn.close()

print("Doublons supprimés !")
