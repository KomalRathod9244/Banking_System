from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Customer:
    id: int
    branch_id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    created_at: datetime

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def from_row(cls, row: tuple[Any, ...]) -> "Customer":
        return cls(
            id=row[0],
            branch_id=row[1],
            first_name=row[2],
            last_name=row[3],
            email=row[4],
            phone=row[5],
            created_at=row[6],
        )
