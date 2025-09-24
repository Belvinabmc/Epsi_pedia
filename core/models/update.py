from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Any
from datetime import datetime

# Table FR attendue : updates
# Colonnes FR : id, resume, date
UPDATE_DB_COLS = {
    "id": "id",
    "resume": "summary",
    "date": "created_at",          # epoch seconds
}

@dataclass(slots=True)
class Update:
    id: int
    summary: str
    created_at: datetime                # epoch seconds

    @staticmethod
    def from_row(row: Mapping[str, Any]) -> "Update":
        return Update(
            id=row["id"],
            summary=row["resume"],
            created_at=row["date"],
        )

    def to_insert_params(self) -> dict[str, Any]:
        return {
            "resume": self.summary,
            "date": self.created_at,
        }

    def to_update_params(self) -> dict[str, Any]:
        return {
            "resume": self.summary,
            "date": self.created_at,
            "id": self.id,  # WHERE id = :id
        }
