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

    # Table tutos (ajout image_path)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS tutos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titre TEXT NOT NULL,
        contenu TEXT NOT NULL,
        image_path TEXT,
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
            ("Faire du feu sans briquet",
             """Allumer un feu est vital pour se réchauffer, purifier l’eau, éloigner les animaux.

Méthodes :
1. **Silex + acier** : frottez pour créer des étincelles sur un nid d’amadou (écorce de bouleau, coton carbonisé).
2. **Arc à feu** : fabriquez un arc avec une corde, une planchette et un foret en bois sec. Le mouvement rotatif crée de la chaleur.
3. **Batterie + laine d’acier** : reliez les deux bornes avec de la laine d’acier → combustion immédiate.

Astuce : préparez toujours trois tailles de bois avant d’allumer.

(mettre photo d’un arc à feu en action)
""", None),

            ("Construire un abri d’urgence",
             """Un abri protège du froid, de la pluie et des prédateurs.

Étapes :
1. Choisissez un endroit sec, légèrement en hauteur.
2. Appuyez une grosse branche contre un tronc → ossature.
3. Ajoutez des branches en pente, puis couvrez de feuilles, mousse ou écorce.
4. Pour isoler le sol, mettez 20 cm de feuilles sèches ou fougères.
5. Fermez l’entrée avec un tissu, peau ou feuillage.

Astuce : évitez les abris trop spacieux → plus difficiles à chauffer.

(mettre photo d’un abri de branches et feuillages)
""", None),

            ("S’orienter sans boussole",
             """Méthodes simples :
- **Avec le soleil** : lever = Est, coucher = Ouest.
- **Avec un bâton** : plantez-le dans le sol, marquez l’ombre. Après 15 min, la nouvelle ombre = Est, la 1ère = Ouest.
- **Avec la lune** : entre 18h et minuit, la face éclairée indique l’Ouest. Après minuit, elle indique l’Est.

(mettre photo d’un bâton et d’une ombre servant de boussole)
""", None),

            ("Filtrer et purifier l’eau",
             """Boire de l’eau contaminée = danger mortel.

Étapes :
1. Filtre artisanal : remplissez une bouteille coupée avec des couches de sable, charbon de bois, et tissu.
2. Faites bouillir l’eau au moins 5 minutes.
3. Si vous avez du soleil : fabriquez un distillateur solaire avec une bâche transparente sur un trou humide.

(mettre photo d’un filtre artisanal avec sable et charbon)
""", None),

            ("Se protéger des animaux",
             """- Gardez le feu allumé la nuit → éloigne la majorité des prédateurs.
- Suspendez vos vivres à un arbre (3m de haut, 2m du tronc).
- Évitez de dormir près des points d’eau : zones de passage des bêtes.
- Faites du bruit en marchant → pour éviter de surprendre un animal.

(mettre photo d’un sac suspendu à un arbre)
""", None),
        ],

        "🥫 Nourriture & ressources": [
            ("Conserver la viande",
             """Pour éviter la putréfaction :
1. Coupez en fines lamelles.
2. Séchez au soleil ou fumez au-dessus d’un feu doux.
3. Ajoutez du sel si disponible.
4. Conservez dans un tissu sec, jamais en plastique fermé.

(mettre photo de viande séchée accrochée sur des branches)
""", None),

            ("Chasse au petit gibier",
             """Le piège le plus simple = collet.

Étapes :
1. Prenez un fil de fer ou corde fine → formez un nœud coulant.
2. Placez-le à 10 cm du sol sur un passage de lapin ou rongeur.
3. Camouflez avec de l’herbe.
4. Vérifiez vos collets chaque matin.

(mettre photo d’un collet installé sur un sentier)
""", None),

            ("Pêche improvisée",
             """Techniques :
- **Hameçon artisanal** : os taillé, épingle, clou plié.
- **Filet de fortune** : chemise ou pantalon noué.
- **Piège en V** : aligner des pierres dans la rivière.

Astuce : les poissons mordent tôt le matin ou au coucher du soleil.

(mettre photo d’un piège en pierres dans une rivière)
""", None),

            ("Insectes comestibles",
             """Source de protéines excellente.

Sûrs : grillons, sauterelles, larves de coléoptères.
À éviter : insectes colorés, qui sentent mauvais ou poilus.

Préparation : faire rôtir ou bouillir → élimine parasites.

(mettre photo de sauterelles grillées sur un feu)
""", None),

            ("Plantes comestibles",
             """Sélection basique :
- **Orties** : riches en fer (cuire).
- **Pissenlits** : tout est comestible.
- **Plantain** : feuilles riches en fibres.
- **Mûres sauvages** : énergie rapide.

Astuce : test d’innocuité universel → frottez une petite partie de plante sur votre bras, attendez 15 min. Si réaction = danger.

(mettre photo d’orties et de pissenlits dans la nature)
""", None),
        ],

        "🩹 Soins & premiers secours": [
            ("Désinfection artisanale",
             """- Eau bouillie (5 min minimum).
- Alcool fort (eau-de-vie, rhum).
- Sève de pin ou miel → antiseptiques naturels.

Astuce : n’utilisez jamais de terre ou d’excréments pour couvrir une plaie !

(mettre photo d’un récipient d’eau bouillante utilisé pour nettoyer une plaie)
""", None),

            ("Pansements maison",
             """1. Nettoyez avec eau bouillie.
2. Placez tissu propre sur la plaie.
3. Maintenez avec ficelle, lianes ou ruban.
4. Changez chaque jour.

Bonus : le miel = antibiotique naturel.

(mettre photo d’un pansement improvisé avec tissu blanc)
""", None),

            ("Réanimation cardio-pulmonaire (RCP)",
             """1. Vérifiez si la personne respire.
2. Placez vos mains au milieu de la poitrine.
3. 30 compressions rapides (100-120/min).
4. Alternez avec 2 insufflations si vous savez faire.

Astuce : rythme du massage = « Stayin’ Alive » des Bee Gees.

(mettre photo d’une démonstration RCP sur mannequin)
""", None),

            ("Soigner une fracture",
             """1. Immobilisez avec deux branches de chaque côté du membre.
2. Attachez avec corde, tissu ou ceinture.
3. Ne pas réaligner si l’os dépasse.

(mettre photo d’une attelle improvisée avec bois et corde)
""", None),

            ("Traiter une morsure de serpent",
             """1. Gardez la victime immobile.
2. Ne pas couper ni aspirer le venin !
3. Mettre un bandage compressif au-dessus de la morsure.
4. Transporter la victime rapidement.

(mettre photo d’un bandage serré au-dessus d’une morsure de jambe)
""", None),
        ],

        "🔋 Énergie & technologie": [
            ("Utiliser une batterie de voiture",
             """1. Bornes : + rouge, - noir.
2. Connectez une ampoule, radio ou petit appareil.
3. Utilisez câbles isolés.
4. Ne jamais court-circuiter.

(mettre photo d’une batterie alimentant une lampe)
""", None),

            ("Fabriquer une bougie",
             """1. Prenez un récipient.
2. Ajoutez de la graisse animale fondue ou de l’huile végétale.
3. Plantez un tissu torsadé comme mèche.

(mettre photo d’une bougie artisanale avec graisse animale)
""", None),

            ("Charger un téléphone avec un feu",
             """Avec une plaque Peltier (thermoélectrique) → transformez chaleur → électricité.

1. Placez la plaque entre une casserole chaude et un dissipateur froid.
2. Branchez un régulateur USB.
3. Téléphone chargé !

(mettre photo d’un chargeur artisanal branché sur un feu)
""", None),

            ("Radio manuelle",
             """Radio à galène = capter sans pile.

Matériel :
- Antenne filaire.
- Cristal de galène.
- Écouteurs haute impédance.

(mettre photo d’une radio à galène bricolée)
""", None),
        ],

        "🛠 Bricolage & outils": [
            ("Fabriquer un couteau",
             """1. Prenez une pierre dure.
2. Frappez-la pour obtenir un éclat tranchant.
3. Fixez-le à un manche avec corde végétale.

(mettre photo d’un couteau en silex monté sur manche bois)
""", None),

            ("Improviser des clous",
             """1. Chauffez métal (boîte conserve).
2. Aplatissez au marteau pierre.
3. Taillez en pointe.

(mettre photo de clous improvisés à partir de métal recyclé)
""", None),

            ("Corde naturelle",
             """1. Prenez fibres (chanvre, orties, écorce).
2. Torsadez-les → ficelle.
3. Doublez-la → corde résistante.

(mettre photo de corde artisanale en fibres végétales)
""", None),

            ("Construire un marteau",
             """1. Pierre lourde ronde.
2. Branche fourchue → manche.
3. Attachez avec corde végétale.

(mettre photo d’un marteau en pierre lié à une branche)
""", None),

            ("Réparer sans électricité",
             """Levier, poulie et cordage = soulever des charges lourdes.

Exemple : trépied en bois avec poulie de corde = grue artisanale.

(mettre photo d’un trépied en bois avec corde)
""", None),
        ],

        "📡 Communication locale": [
            ("Signaux de fumée",
             """1. Feu de base + feuilles vertes = fumée dense.
2. Trois colonnes successives = SOS.
3. Couvrir/découvrir pour varier les signaux.

(mettre photo de signaux de fumée visibles dans une clairière)
""", None),

            ("Code Morse",
             """Système universel :
- Point = signal court
- Trait = signal long

Exemple : SOS = ... --- ...

Transmettez avec lampe, coups sur métal ou sifflet.

(mettre photo d’une lampe utilisée en morse)
""", None),

            ("Balises improvisées",
             """Disposez pierres, bois ou vêtements pour former :
- Flèche = direction
- Croix = danger
- Cercle = camp

(mettre photo de pierres en forme de flèche au sol)
""", None),

            ("Reflets du soleil",
             """Un miroir ou métal poli = signal lumineux.

1. Orientez le reflet vers l’objectif (montagne, avion).
2. Mouvements rapides pour attirer attention.

(mettre photo d’une personne signalant avec miroir)
""", None),

            ("Tambours et sons",
             """Battez un rythme régulier → utilisé par de nombreux peuples pour transmettre des infos.

Exemple : rythme rapide = danger / lente = appel au camp.

(mettre photo d’un tambour improvisé en bois et peau)
""", None),
        ]
    }

    # Insérer catégories et tutos
    for cat in categories:
        cur.execute("INSERT OR IGNORE INTO categories (nom) VALUES (?)", (cat,))
        cur.execute("SELECT id FROM categories WHERE nom = ?", (cat,))
        cat_id = cur.fetchone()[0]

        for titre, contenu, image_path in exemples[cat]:
            cur.execute("""
            INSERT INTO tutos (titre, contenu, image_path, categorie_id)
            VALUES (?, ?, ?, ?)
            """, (titre, contenu, image_path, cat_id))

    conn.commit()
    # Suppression automatique des doublons (ne garde que le tuto avec l'id le plus bas pour chaque titre)
    conn.execute('''
        DELETE FROM tutos
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM tutos
            GROUP BY titre
        )
    ''')
    conn.commit()
    conn.close()




# --- Bloc d'exécution automatique ---
if __name__ == "__main__":
    init_db()
    peupler_exemples()

