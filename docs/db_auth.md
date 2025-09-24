# Schéma DB & règles d’auth

## Table `utilisateurs`
- `id` : INTEGER, PRIMARY KEY AUTOINCREMENT
- `nom_utilisateur` : TEXT, UNIQUE, NOT NULL
- `mot_de_passe_hachage` : TEXT, NOT NULL (Argon2id)
- `role` : TEXT, NOT NULL, CHECK (`role` IN ('admin','user'))
- `tentatives_echouees` : INTEGER, NOT NULL DEFAULT 0
- `verrouille_jusqua` : INTEGER (timestamp epoch, secondes)

## Politiques de sécurité
- Hachage : **Argon2id** (jamais de mot de passe en clair).
- Anti brute-force : **5 échecs consécutifs → verrouillage 10 min**.
- Politique MDP : **≥ 8 caractères** (ou passphrase courte).
- Compte admin par défaut : créé automatiquement s’il est absent.
  - **Mot de passe temporaire** (à changer) : `ChangeMe123!`

## Événements à journaliser
- Fichier : `storage/security.log`
- Format recommandé : `ISO8601 | username | event | details`
- Événements :
  - `LOGIN_FAILED` — détails : tentative n°, IP si dispo
  - `ACCOUNT_LOCKED` — détails : `until=<ISO8601>`
  - `PASSWORD_CHANGED` — détails : initiateur (`self`|`admin`)
