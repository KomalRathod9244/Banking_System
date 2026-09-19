from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass
class Account:
    id: int
    customer_id: int
    branch_id: int
    account_number: str
    account_type: str
    balance: Decimal
    status: str
    created_at: datetime

    @classmethod
    def from_row(cls, row: tuple[Any, ...]) -> "Account":
        return cls(
            id=row[0],
            customer_id=row[1],
            branch_id=row[2],
            account_number=row[3],
            account_type=row[4],
            balance=Decimal(str(row[5])),
            status=row[6],
            created_at=row[7],
        )
