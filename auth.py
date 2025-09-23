# auth.py

def verifier_code(code: str) -> bool:
    """
    Vérifie si le code est valide pour accéder à Epsipédia.
    """
    return code == "1234"


def est_admin(code: str) -> bool:
    """
    Vérifie si l'utilisateur est admin.
    On peut imaginer un autre code admin plus tard.
    """
    return code == "admin"
