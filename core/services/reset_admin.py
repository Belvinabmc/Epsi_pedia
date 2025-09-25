# reset_admin.py — remet à zéro le compte admin (mot de passe + TOTP)
import json, sys
from pathlib import Path

try:
    import keyring
except Exception as e:
    print("[!] keyring manquant :", e, "\nInstallez-le: pip install keyring")
    sys.exit(1)

# 1) Supprimer les secrets/mot de passe dans le gestionnaire Windows
SERVICE = "Epsipedia"
USER    = "admin"
try:
    keyring.delete_password(SERVICE, USER)
    print("[OK] Mot de passe admin supprimé du keyring.")
except keyring.errors.PasswordDeleteError:
    print("[i] Aucune entrée keyring à supprimer (déjà vide).")
except Exception as e:
    print("[!] Erreur keyring :", e)

# 2) Supprimer le fichier local qui marque l'initialisation + stocke le secret TOTP
#    (selon la version, le fichier peut s'appeler admin.json ou admin_auth.json)
candidates = [
    Path("storage") / "admin.json",
    Path("storage") / "admin_auth.json",
    Path("storage") / "admin" / "admin.json",
]
done = False
for p in candidates:
    if p.exists():
        try:
            p.unlink()
            print(f"[OK] Supprimé : {p}")
            done = True
        except Exception as e:
            print(f"[!] Impossible de supprimer {p} :", e)

if not done:
    print("[i] Aucun fichier admin.json/admin_auth.json trouvé (déjà réinitialisé).")

print("\n=> Relancez:  python main.py")
print("Vous verrez la fenêtre 'Initialiser l’administrateur'.")
print("Créez un nouveau mot de passe, notez le SECRET TOTP affiché,")
print("ajoutez-le dans votre application d’authentification, puis connectez-vous.")