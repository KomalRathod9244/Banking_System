from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any


@dataclass
class LoanPayment:
    id: int
    loan_id: int
    amount: Decimal
    outstanding_after: Decimal
    created_at: datetime

    @classmethod
    def from_row(cls, row: tuple[Any, ...]) -> "LoanPayment":
        return cls(
            id=row[0],
            loan_id=row[1],
            amount=Decimal(str(row[2])),
            outstanding_after=Decimal(str(row[3])),
            created_at=row[4],
        )
