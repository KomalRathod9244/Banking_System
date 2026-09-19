from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Bank:
    id: int
    name: str
    code: str
    created_at: datetime

    @classmethod
    def from_row(cls, row: tuple[Any, ...]) -> "Bank":
        return cls(
            id=row[0],
            name=row[1],
            code=row[2],
            created_at=row[3],
        )
