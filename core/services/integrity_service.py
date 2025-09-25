# core/services/integrity_service.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List
import hashlib, json, time

from core.config import ASSETS, MANIFEST_PATH, ALLOWED_EXT
from core.services.security_logger import log_event

CHUNK = 1024 * 1024  # 1 Mo

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(CHUNK), b""):
            h.update(chunk)
    return h.hexdigest()

@dataclass
class VerifyReport:
    ok: bool
    added: List[str]
    missing: List[str]
    changed: List[str]
    bad_ext: List[str]

class IntegrityService:
    """
    - (Re)construit le manifest (SHA-256) des fichiers autorisés
    - Compare l'état courant vs manifest
    - Active lecture_seule si anomalie
    - Expose is_safe(path) pour filtrer l’UI
    """
    def __init__(self) -> None:
        self.assets: Path = ASSETS
        self.manifest_path: Path = MANIFEST_PATH
        self.lecture_seule: bool = False
        self._manifest: Dict = self._load_manifest()

    # ----- manifest -----
    def _load_manifest(self) -> Dict:
        if self.manifest_path.exists():
            try:
                return json.loads(self.manifest_path.read_text(encoding="utf-8"))
            except Exception:
                log_event("MANIFEST", "manifest illisible → lecture_seule")
                self.lecture_seule = True
        return {"generated_at": None, "files": {}}

    def _save_manifest(self, data: Dict) -> None:
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def rebuild_manifest(self) -> int:
        files: Dict[str, Dict] = {}
        count = 0
        for p in self.assets.rglob("*"):
            if p.is_file() and self._is_in_assets(p) and p.suffix.lower() in ALLOWED_EXT:
                rel = str(p.relative_to(self.assets)).replace("\\", "/")
                files[rel] = {"sha256": sha256_file(p), "size": p.stat().st_size}
                count += 1
        data = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "files": files}
        self._save_manifest(data)
        self._manifest = data
        self.lecture_seule = False
        log_event("MANIFEST_REBUILD", f"{count} fichiers indexés")
        return count

    # ----- vérification -----
    def verify(self) -> VerifyReport:
        added:   List[str] = []
        missing: List[str] = []
        changed: List[str] = []
        bad_ext: List[str] = []

        files = self._manifest.get("files", {})
        seen = set()

        for p in self.assets.rglob("*"):
            if not p.is_file():
                continue
            rel = str(p.relative_to(self.assets)).replace("\\", "/")

            # hors sandbox ou extension interdite
            if not self._is_in_assets(p) or p.suffix.lower() not in ALLOWED_EXT:
                bad_ext.append(rel)
                continue

            seen.add(rel)

            if rel not in files:
                added.append(rel)
            else:
                if (files[rel]["sha256"] != sha256_file(p)
                        or files[rel]["size"] != p.stat().st_size):
                    changed.append(rel)

        for rel in files.keys():
            if rel not in seen:
                missing.append(rel)

        # ---- LOG DÉTAILLÉ ICI (à l'intérieur de verify) ----
        for rel in added:
            log_event("FILE_ADDED", rel)
        for rel in missing:
            log_event("FILE_MISSING", rel)
        for rel in changed:
            log_event("FILE_CHANGED", rel)
        for rel in bad_ext:
            log_event("BAD_EXT", rel)

        ok = (not added and not missing and not changed and not bad_ext)
        self.lecture_seule = not ok

        if ok:
            log_event("INTEGRITY", "OK (manifest conforme)")
        else:
            log_event(
                "INTEGRITY",
                f"KO added={len(added)} missing={len(missing)} changed={len(changed)} bad_ext={len(bad_ext)}"
            )

        return VerifyReport(ok=ok, added=added, missing=missing, changed=changed, bad_ext=bad_ext)

    def is_safe(self, path: Path) -> bool:
        try:
            path = path.resolve()
            if not self._is_in_assets(path) or path.suffix.lower() not in ALLOWED_EXT:
                return False
            rel = str(path.relative_to(self.assets)).replace("\\", "/")
            files = self._manifest.get("files", {})
            if rel not in files:
                return False
            return (files[rel]["sha256"] == sha256_file(path)
                    and files[rel]["size"] == path.stat().st_size)
        except Exception:
            return False

    # ----- util -----
    def _is_in_assets(self, p: Path) -> bool:
        try:
            return self.assets in p.resolve().parents
        except Exception:
            return False
