# core/services/admin_auth.py
from __future__ import annotations

import json, os
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, Optional

import keyring
import pyotp
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from core.config import STORAGE_PATH

import random
import time

def generate_offline_code():
    # Nouveau code toutes les 30 secondes
    random.seed(int(time.time()) // 30)
    return str(random.randint(100000, 999999))


AUTH_FILE = STORAGE_PATH / "admin_auth.json"
KEYRING_SERVICE = "Epsipedia_Admin"
KEYRING_ITEM = "totp_secret"

ph = PasswordHasher()

@dataclass
class AdminMeta:
    pw_hash: str
    keyring_service: str
    keyring_item: str

def _read_meta() -> Optional[AdminMeta]:
    if not AUTH_FILE.exists():
        return None
    try:
        data = json.loads(AUTH_FILE.read_text(encoding="utf-8"))
        return AdminMeta(
            pw_hash=data["pw_hash"],
            keyring_service=data.get("keyring_service", KEYRING_SERVICE),
            keyring_item=data.get("keyring_item", KEYRING_ITEM),
        )
    except Exception:
        return None

def _write_meta(meta: AdminMeta) -> None:
    AUTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    AUTH_FILE.write_text(json.dumps({
        "pw_hash": meta.pw_hash,
        "keyring_service": meta.keyring_service,
        "keyring_item": meta.keyring_item,
    }, indent=2), encoding="utf-8")

def is_initialized() -> bool:
    meta = _read_meta()
    if not meta:
        return False
    # secret doit exister dans le trousseau
    secret = keyring.get_password(meta.keyring_service, meta.keyring_item)
    return bool(secret)

def initialize_admin(password: str) -> Tuple[str, str]:
    """
    Initialise l'admin :
      - hash Argon2 du mot de passe
      - secret TOTP généré et stocké dans le trousseau OS via keyring
      - écrit un petit JSON avec le hash (pas de secret !)

    Retourne (secret, otpauth_url) pour que l’admin l’ajoute dans son appli.
    """
    # 1) hash du mot de passe
    pw_hash = ph.hash(password)

    # 2) secret TOTP aléatoire
    secret = pyotp.random_base32()

    # 3) stocke le secret dans le trousseau
    keyring.set_password(KEYRING_SERVICE, KEYRING_ITEM, secret)

    # 4) écrit le fichier méta (hash seulement)
    _write_meta(AdminMeta(pw_hash=pw_hash, keyring_service=KEYRING_SERVICE, keyring_item=KEYRING_ITEM))

    # 5) URL otpauth pour scanner (ou saisir la clé)
    otpauth_url = pyotp.totp.TOTP(secret).provisioning_uri(
        name="admin@epsipedia",
        issuer_name="Epsipedia"
    )
    return secret, otpauth_url

def verify_admin(password: str, totp_code: str) -> Tuple[bool, str]:
    """
    Vérifie => (OK?, message)
    """
    meta = _read_meta()
    if not meta:
        return (False, "Admin non initialisé")

    # 1) mot de passe
    try:
        ph.verify(meta.pw_hash, password)
    except VerifyMismatchError:
        return (False, "Mot de passe incorrect")
    except Exception:
        return (False, "Erreur de vérification du mot de passe")

    # 2) TOTP à 6 chiffres
    secret = keyring.get_password(meta.keyring_service, meta.keyring_item)
    if not secret:
        return (False, "Secret TOTP introuvable (trousseau)")

    try:
        totp = pyotp.TOTP(secret)
        if not totp.verify(totp_code, valid_window=1):
            return (False, "Code TOTP invalide")
    except Exception:
        return (False, "Erreur TOTP")

    return (True, "OK")

def change_admin_password(old_password: str, new_password: str) -> Tuple[bool, str]:
    meta = _read_meta()
    if not meta:
        return (False, "Admin non initialisé")
    try:
        ph.verify(meta.pw_hash, old_password)
    except Exception:
        return (False, "Ancien mot de passe incorrect")
    new_hash = ph.hash(new_password)
    _write_meta(AdminMeta(pw_hash=new_hash, keyring_service=meta.keyring_service, keyring_item=meta.keyring_item))
    return (True, "Mot de passe changé")

def rotate_totp_secret() -> Tuple[bool, str]:
    meta = _read_meta()
    if not meta:
        return (False, "Admin non initialisé")
    secret = pyotp.random_base32()
    keyring.set_password(meta.keyring_service, meta.keyring_item, secret)
    return (True, secret)
