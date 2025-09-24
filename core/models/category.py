from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Mapping, Any

# Table FR attendue : categories
# Colonnes FR : nom (PK TEXT), description
CATEGORY_DB_COLS = {
    "nom": "name",
    "description": "description",
}

@dataclass(slots=True)
class Category:
    name: str
    description: Optional[str] = None

    @staticmethod
    def from_row(row: Mapping[str, Any]) -> "Category":
        return Category(
            name=row["nom"],
            description=row["description"],
        )

    def to_insert_params(self) -> dict[str, Any]:
        return {
            "nom": self.name,
            "description": self.description,
        }

    def to_update_params(self) -> dict[str, Any]:
        return {
            "description": self.description,
            "nom": self.name,  # pour WHERE nom = :nom
        }
