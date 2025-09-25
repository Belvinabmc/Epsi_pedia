# database.py
import sqlite3

DB_NAME = "database2.db"

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
            ("Faire du feu",
             "Méthode de base : préparez un nid d’amadou (herbes sèches, écorce fine). "
             "Avec un silex, une batterie + laine d’acier ou un arc à feu, produisez des étincelles. "
             "Soufflez doucement pour embraser l’amadou, puis ajoutez des brindilles, puis des branches."),
            ("Trouver de l’eau",
             "Cherchez la rosée du matin en frottant un tissu sur l’herbe, utilisez des trous solaires (bâche transparente au-dessus d’un trou rempli de végétaux). "
             "Les rivières se trouvent souvent dans les vallées, et certains bambous contiennent de l’eau potable."),
            ("Construire un abri",
             "Un abri simple : appuyez une grande branche contre un arbre pour former une ossature. "
             "Recouvrez de branches plus petites, puis de feuillages ou d’écorce pour l’isolation. "
             "Le sol doit être isolé avec des feuilles sèches ou des fougères."),
            ("S’orienter avec le soleil",
             "Le soleil se lève à l’est et se couche à l’ouest. "
             "En plantant un bâton dans le sol, marquez l’extrémité de l’ombre : c’est l’ouest. "
             "Quelques minutes plus tard, la nouvelle ombre indiquera l’est."),
        ],

        "🥫 Nourriture & ressources": [
            ("Conserver la viande",
             "Découpez la viande en fines lanières. Suspendez-les au-dessus d’un feu de bois pour les fumer, ou laissez-les sécher au soleil. "
             "Ajoutez du sel si possible pour ralentir la prolifération bactérienne."),
            ("Techniques de pêche",
             "Fabriquez un hameçon avec une épingle ou un os taillé. "
             "Creusez des pièges en V avec des pierres au bord de l’eau. "
             "Les filets improvisés peuvent être faits avec des vêtements ou des fibres végétales."),
            ("Plantes comestibles",
             "Les pissenlits (fleurs jaunes), orties (cuisinées, elles perdent leurs poils urticants), et plantain (feuilles larges nervurées) sont sûrs et nutritifs. "
             "Évitez toujours les plantes au goût amer, à sève blanche ou aux baies rouges."),
            ("Chasse au petit gibier",
             "Fabriquez un collet avec du fil ou de la corde fine, et placez-le sur un passage fréquenté (traces au sol). "
             "Camouflez-le avec de la végétation."),
        ],

        "🩹 Soins & premiers secours": [
            ("Pansements maison",
             "Utilisez un tissu propre plié en plusieurs couches, maintenu avec des lianes, des cordes ou du ruban. "
             "Le miel peut être appliqué sur la plaie comme antibactérien naturel."),
            ("Gérer une blessure",
             "En cas d’hémorragie, appliquez une compression directe. "
             "Si ça ne suffit pas, placez un garrot au-dessus de la plaie (entre le cœur et la blessure)."),
            ("Désinfection",
             "Faites bouillir de l’eau pendant au moins 5 minutes. "
             "Utilisez de l’alcool (alcool de bois, fort alcool de consommation si disponible) pour nettoyer les plaies. "
             "À défaut, la sève de certaines plantes (comme le pin) a des propriétés antiseptiques."),
            ("Réanimation cardio-pulmonaire (RCP)",
             "Si une personne ne respire plus : placez vos mains l’une sur l’autre au milieu de sa poitrine. "
             "Appuyez fermement 100 à 120 fois par minute, en alternant avec 2 insufflations si vous êtes formé."),
        ],

        "🔋 Énergie & technologie": [
            ("Fabriquer une dynamo",
             "Fixez une dynamo de vélo contre une roue. Branchez-la à une petite ampoule LED ou à une batterie pour stockage."),
            ("Utiliser une batterie de voiture",
             "Les batteries 12V peuvent alimenter des lampes, radios ou même des résistances chauffantes. "
             "Attention : toujours utiliser des câbles isolés et éviter le court-circuit."),
            ("Radio manuelle",
             "Une radio à galène peut être fabriquée avec une antenne filaire, un cristal de galène et un écouteur à haute impédance. "
             "Cela permet d’écouter certaines fréquences locales sans électricité externe."),
            ("Charger un téléphone avec un feu",
             "Un générateur thermoélectrique (style Peltier) peut transformer la chaleur du feu en électricité. "
             "Certains bricolages permettent d’improviser un chargeur basique."),
        ],

        "🛠 Bricolage & outils": [
            ("Fabriquer un couteau",
             "Trouvez une pierre dure (silex, obsidienne). Frappez-la pour obtenir un éclat tranchant. "
             "Fixez-le à un manche en bois avec des fibres végétales ou de la résine."),
            ("Réparer sans électricité",
             "Les leviers, poulies et systèmes de cordes permettent de soulever de lourdes charges. "
             "Un trépied avec des cordes peut servir de grue artisanale."),
            ("Improviser des clous",
             "Cherchez du métal (boîtes de conserve, ferrailles). Chauffez-les dans un feu, aplatissez-les puis taillez-les en pointes."),
            ("Corde naturelle",
             "Les fibres de chanvre, d’ortie ou d’écorce torsadées peuvent former des cordes solides. "
             "Enroulez-les sur elles-mêmes puis doublez-les pour plus de résistance."),
        ],

        "📡 Communication locale": [
            ("Signaux de fumée",
             "Faites un feu et couvrez-le par intermittence avec une couverture humide pour créer des colonnes de fumée. "
             "Trois colonnes = appel de détresse."),
            ("Code Morse",
             "Un point = signal court, un trait = signal long. "
             "Avec une lampe ou en frappant sur un objet métallique, vous pouvez transmettre des messages. "
             "Exemple : SOS = ... --- ..."),
            ("Balises improvisées",
             "Disposez des pierres, branches ou objets visibles en forme de flèche au sol pour indiquer une direction. "
             "Un cercle = campement, une croix = danger."),
            ("Reflets du soleil",
             "Un miroir, un bout de métal poli ou même un écran de téléphone peut servir de signal lumineux. "
             "Dirigez le reflet vers une montagne, un avion ou un camp."),
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
