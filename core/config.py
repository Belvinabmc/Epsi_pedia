# core/config.py
from pathlib import Path

# Racine du projet
ROOT = Path(__file__).resolve().parents[1]

# Dossiers principaux
ASSETS = ROOT / "assets" / "content"          # contenus navigués par l'UI
STORAGE_PATH = ROOT / "storage"               # tout ce qui est écrit
IMPORT_TMP = STORAGE_PATH / "_import_tmp"     # <- tampon pour imports .epk

# Fichiers de stockage
MANIFEST_PATH = STORAGE_PATH / "manifest.json"
SECURITY_LOG_PATH = STORAGE_PATH / "security.log"

# Extensions autorisées
ALLOWED_EXT = {".txt", ".md", ".pdf", ".jpg", ".jpeg", ".png", ".mp4"}

# (optionnel) libellés UI des catégories si tu en as besoin ici
CATEGORIES = {
    "survie": "🪵 Survie en milieu naturel",
    "nourriture": "🥫 Nourriture & ressources",
    "soins": "🩹 Soins & premiers secours",
    "energie": "🔋 Énergie & technologie",
    "bricolage": "🛠 Bricolage & outils",
    "communication": "📡 Communication locale",
}

# Crée les répertoires au besoin
for p in (ASSETS, STORAGE_PATH, IMPORT_TMP):
    p.mkdir(parents=True, exist_ok=True)

# Crée les fichiers si absents
if not MANIFEST_PATH.exists():
    MANIFEST_PATH.write_text('{"generated_at": null, "files": {}}', encoding="utf-8")
if not SECURITY_LOG_PATH.exists():
    SECURITY_LOG_PATH.write_text("", encoding="utf-8")
