from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal, Mapping, Any

Role = Literal["admin", "user"]

# Mapping DB (FR) ↔ domaine (EN)
DB_COLS = {
    "id": "id",
    "nom_utilisateur": "username",
    "mot_de_passe_hachage": "pw_hash",
    "role": "role",
    "tentatives_echouees": "failed_attempts",
    "verrouille_jusqua": "lock_until",
}

@dataclass(slots=True)
class User:
    id: int
    username: str
    pw_hash: str
    role: Role
    failed_attempts: int = 0
    lock_until: Optional[int] = None  # epoch seconds

    # ——— Factories ———
    @staticmethod
    def from_row(row: Mapping[str, Any]) -> "User":
        """Crée un User depuis une ligne SQLite (dict ou sqlite3.Row)."""
        return User(
            id=row["id"],
            username=row["nom_utilisateur"],
            pw_hash=row["mot_de_passe_hachage"],
            role=row["role"],
            failed_attempts=row["tentatives_echouees"],
            lock_until=row["verrouille_jusqua"],
        )

    def to_insert_params(self) -> dict[str, Any]:
        """Params pour INSERT dans la table `utilisateurs`."""
        return {
            "nom_utilisateur": self.username,
            "mot_de_passe_hachage": self.pw_hash,
            "role": self.role,
            "tentatives_echouees": self.failed_attempts,
            "verrouille_jusqua": self.lock_until,
        }

    def to_update_security_params(self) -> dict[str, Any]:
        """Params pour UPDATE des compteurs/verrouillage."""
        return {
            "tentatives_echouees": self.failed_attempts,
            "verrouille_jusqua": self.lock_until,
            "nom_utilisateur": self.username,  # souvent en WHERE
        }


@dataclass(slots=True)
class UserCreate:
    """Payload pour créer un utilisateur (avant INSERT)."""
    username: str
    pw_hash: str
    role: Role = "user"

    def to_insert_params(self) -> dict[str, Any]:
        return {
            "nom_utilisateur": self.username,
            "mot_de_passe_hachage": self.pw_hash,
            "role": self.role,
        }
