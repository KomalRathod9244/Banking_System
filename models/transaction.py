from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional


@dataclass
class Transaction:
    id: int
    account_id: int
    transaction_type: str
    amount: Decimal
    balance_after: Decimal
    description: Optional[str]
    created_at: datetime

    @classmethod
    def from_row(cls, row: tuple[Any, ...]) -> "Transaction":
        return cls(
            id=row[0],
            account_id=row[1],
            transaction_type=row[2],
            amount=Decimal(str(row[3])),
            balance_after=Decimal(str(row[4])),
            description=row[5],
            created_at=row[6],
        )
