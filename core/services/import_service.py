# core/services/import_service.py
from __future__ import annotations

import json, zipfile, shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

from core.config import ALLOWED_EXT, ASSETS, MANIFEST_PATH, IMPORT_TMP, STORAGE_PATH
from core.services.security_logger import log_event
from core.services.integrity_service import IntegrityService

@dataclass
class ImportReport:
    ok: bool
    reason: str
    added: List[str]
    skipped_bad: List[str]

class ImportService:
    """
    Importe un paquet .epk (zip) contenant:
      - manifest.json
      - content/...
    Étapes: dézipper en /storage/import_tmp -> vérifier -> copier vers assets/content -> reconstruire manifest.
    """

    def __init__(self) -> None:
        IMPORT_TMP.mkdir(parents=True, exist_ok=True)
        STORAGE_PATH.mkdir(parents=True, exist_ok=True)

    def _clean_tmp(self) -> None:
        if IMPORT_TMP.exists():
            shutil.rmtree(IMPORT_TMP, ignore_errors=True)
        IMPORT_TMP.mkdir(parents=True, exist_ok=True)

    def import_epk(self, epk_path: Path) -> ImportReport:
        epk_path = Path(epk_path)
        if not epk_path.exists() or epk_path.suffix.lower() != ".epk":
            return ImportReport(False, "Fichier .epk invalide", [], [])

        self._clean_tmp()

        # 1) Dézipper en /storage/import_tmp
        try:
            with zipfile.ZipFile(epk_path, "r") as z:
                z.extractall(IMPORT_TMP)
        except Exception as e:
            log_event("IMPORT_FAIL", f"zip illisible: {e}")
            return ImportReport(False, "Paquet corrompu (zip)", [], [])

        # 2) Présence des éléments attendus
        tmp_manifest = IMPORT_TMP / "manifest.json"
        tmp_content  = IMPORT_TMP / "content"
        if not tmp_manifest.exists() or not tmp_content.exists():
            log_event("IMPORT_FAIL", "structure manquante (manifest.json/content/)")
            return ImportReport(False, "Structure .epk invalide", [], [])

        # 3) Lire le manifest du paquet
        try:
            m = json.loads(tmp_manifest.read_text(encoding="utf-8"))
            files = m.get("files", {})
            if not isinstance(files, dict):
                raise ValueError("champ files manquant ou invalide")
        except Exception as e:
            log_event("IMPORT_FAIL", f"manifest.json invalide: {e}")
            return ImportReport(False, "manifest.json invalide", [], [])

        # 4) Vérifications: chemins + extensions + empreintes
        added: List[str] = []
        skipped_bad: List[str] = []
        for rel, meta in files.items():
            rel_path = rel.replace("\\", "/")
            src = (tmp_content / rel_path).resolve()

            # a) le fichier doit exister dans le paquet
            if not src.exists() or not src.is_file():
                skipped_bad.append(rel_path)
                continue

            # b) chemin sandboxé sous content/ (sécurité path traversal)
            try:
                if tmp_content not in src.parents:
                    skipped_bad.append(rel_path)
                    continue
            except Exception:
                skipped_bad.append(rel_path)
                continue

            # c) extension whitelistée
            if src.suffix.lower() not in ALLOWED_EXT:
                skipped_bad.append(rel_path)
                continue

            # d) hash/size conforme au manifest du paquet
            from core.services.integrity_service import sha256_file
            ok_hash = (meta.get("sha256") == sha256_file(src))
            ok_size = (meta.get("size")   == src.stat().st_size)
            if not (ok_hash and ok_size):
                skipped_bad.append(rel_path)
                continue

            # 5) Si tout est OK → copie vers assets/content
            dst = (ASSETS / rel_path).resolve()
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            added.append(rel_path)

        # 6) Journalisation + rebuild manifest principal
        #    NB: on reconstruit le manifest de l’appli (pas celui du paquet)
        integrity = IntegrityService()
        count = integrity.rebuild_manifest()
        log_event("IMPORT_DONE", f"{len(added)} fichiers copiés; skipped={len(skipped_bad)}; manifest={count} items")

        ok = len(added) > 0 and len(skipped_bad) == 0
        reason = "Import partiel" if (added and skipped_bad) else ("OK" if ok else "Rien importé")
        return ImportReport(ok, reason, added, skipped_bad)
