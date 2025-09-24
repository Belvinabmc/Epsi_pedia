from dataclasses import dataclass

# Erreurs “métier” standardisées pour l’auth/Repo
USER_NOT_FOUND = "USER_NOT_FOUND"
USERNAME_TAKEN = "USERNAME_TAKEN"
INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
ACCOUNT_LOCKED = "ACCOUNT_LOCKED"

@dataclass(slots=True)
class DomainError:
    code: str
    message: str
