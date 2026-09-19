from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class Branch:
    id: int
    bank_id: int
    name: str
    address: Optional[str]
    phone: Optional[str]
    created_at: datetime

    @classmethod
    def from_row(cls, row: tuple[Any, ...]) -> "Branch":
        return cls(
            id=row[0],
            bank_id=row[1],
            name=row[2],
            address=row[3],
            phone=row[4],
            created_at=row[5],
        )
