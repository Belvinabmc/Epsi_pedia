from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Mapping, Any
from datetime import datetime

# Table FR attendue : articles
# Colonnes FR : id, titre, contenu, date, categorie_nom (NULL autorisé)
ARTICLE_DB_COLS = {
    "id": "id",
    "titre": "title",
    "contenu": "content",
    "date": "created_at",          # epoch seconds
    "categorie_nom": "category_name",
}

@dataclass(slots=True)
class Article:
    id: int
    title: str
    content: str
    created_at: datetime               # epoch seconds
    category_name: Optional[str] = None  # FK vers categories.nom

    @staticmethod
    def from_row(row: Mapping[str, Any]) -> "Article":
        return Article(
            id=row["id"],
            title=row["titre"],
            content=row["contenu"],
            created_at=row["date"],
            category_name=row["categorie_nom"] if "categorie_nom" in row.keys() else None,
        )

    def to_insert_params(self) -> dict[str, Any]:
        return {
            "titre": self.title,
            "contenu": self.content,
            "date": self.created_at,
            "categorie_nom": self.category_name,
        }

    def to_update_params(self) -> dict[str, Any]:
        return {
            "titre": self.title,
            "contenu": self.content,
            "date": self.created_at,
            "categorie_nom": self.category_name,
            "id": self.id,  # pour WHERE id = :id
        }
