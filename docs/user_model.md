# Modèle métier `User`

## Attributs (code EN) ↔ Mapping DB (FR)
- `id: int` ↔ `id`
- `username: str` ↔ `nom_utilisateur`
- `pw_hash: str` ↔ `mot_de_passe_hachage`
- `role: Literal['admin','user']` ↔ `role`
- `failed_attempts: int` ↔ `tentatives_echouees`
- `lock_until: Optional[int]` (epoch sec) ↔ `verrouille_jusqua`

## Notes
- `username` unique.
- `pw_hash` toujours Argon2id.
- `lock_until` = timestamp de fin de verrouillage (None si non verrouillé).
