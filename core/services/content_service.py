# core/services/content_service.py
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from core.config import ASSETS, ALLOWED_EXT, CATEGORIES

def kind_from_ext(ext: str) -> str:
    e = ext.lower()
    if e in (".txt", ".md"):           return "text"
    if e in (".jpg", ".jpeg", ".png"): return "image"
    if e == ".mp4":                     return "video"
    if e == ".pdf":                     return "pdf"
    return "unknown"

@dataclass
class ContentItem:
    name: str
    path: Path
    rel: str
    ext: str
    kind: str
    size: int

class ContentService:
    def __init__(self, integrity=None):
        self.base = ASSETS
        self.integrity = integrity  # peut rester None

    def list_categories(self) -> Dict[str, str]:
        return CATEGORIES

    def _allowed(self, p: Path) -> bool:
        try:
            p = p.resolve()
            if self.base not in p.parents:
                return False
            if p.suffix.lower() not in ALLOWED_EXT:
                return False
            if self.integrity and not self.integrity.is_safe(p):
                return False
            return True
        except Exception:
            return False

    def list_items(self, category_key: str) -> List[ContentItem]:
        folder = (self.base / category_key)
        items: List[ContentItem] = []
        if not folder.exists() or not folder.is_dir():
            return items
        for f in sorted(folder.rglob("*")):
            if f.is_file() and self._allowed(f):
                items.append(ContentItem(
                    name=f.stem,
                    path=f,
                    rel=str(f.relative_to(self.base)).replace("\\", "/"),
                    ext=f.suffix.lower(),
                    kind=kind_from_ext(f.suffix),
                    size=f.stat().st_size
                ))
        return items

    def read_text(self, item: ContentItem) -> Optional[str]:
        if item.kind != "text":
            return None
        try:
            return item.path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return None
