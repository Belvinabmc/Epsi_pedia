# core/services/auth_service.py
import time
from dataclasses import dataclass
from typing import Optional
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from core.repositories.user_repository import UserRepository
from core.services.security_logger import log_event

LOCK_AFTER = 5          # 5 erreurs avant blocage
LOCK_DURATION = 10*60   # 10 minutes

ph = PasswordHasher()


@dataclass
class AuthResult:
    success: bool
    message: str
    role: Optional[str] = None


class AuthService:
    def __init__(self, repo: Optional[UserRepository] = None):
        self.repo = repo or UserRepository()

    # À appeler une seule fois au démarrage de l’app
    def bootstrap_admin(self):
        admin_hash = ph.hash("admin123")  # mot de passe par défaut
        self.repo.ensure_default_admin(admin_hash)
        log_event("AUTH_INIT", "admin par défaut créé (si absent)")

    def login(self, username: str, password: str) -> AuthResult:
        user = self.repo.get_by_username(username)
        if not user:
            log_event("AUTH_FAIL", f"user inconnu: {username}")
            return AuthResult(False, "Utilisateur inconnu")

        now = int(time.time())
        if user["lock_until"] and user["lock_until"] > now:
            minutes = max(1, int((user["lock_until"] - now) / 60))
            log_event("AUTH_LOCK", f"tentative sur {username} mais compte verrouillé")
            return AuthResult(False, f"Compte verrouillé, réessayez dans ~{minutes} min")

        # Vérification du hash Argon2
        try:
            ph.verify(user["pw_hash"], password)
        except VerifyMismatchError:
            failed = int(user["failed_attempts"]) + 1
            lock_until = 0
            msg = "Mot de passe incorrect"
            if failed >= LOCK_AFTER:
                lock_until = now + LOCK_DURATION
                msg = "Compte verrouillé, réessayez dans ~10 min"
                log_event("AUTH_LOCK", f"{username} verrouillé 10 min (5 échecs)")
                failed = 0  # reset du compteur
            self.repo.update_attempts_and_lock(username, failed, lock_until)
            log_event("AUTH_FAIL", f"user={username} mauvais mot de passe ({failed}/5)")
            return AuthResult(False, msg)

        # Succès
        self.repo.reset_attempts(username)
        log_event("AUTH_OK", f"{username} connecté (role={user['role']})")
        return AuthResult(True, "Connexion réussie", role=user["role"])
