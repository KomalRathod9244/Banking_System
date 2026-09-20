from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, ClassVar, Optional


@dataclass
class Loan:
    id: int
    customer_id: int
    branch_id: int
    account_id: Optional[int]
    loan_type: str
    principal: Decimal
    interest_rate: Decimal
    tenure_months: int
    emi: Decimal
    outstanding: Decimal
    status: str
    created_at: datetime
    approved_at: Optional[datetime]
    disbursed_at: Optional[datetime]

    @classmethod
    def from_row(cls, row: tuple[Any, ...]) -> "Loan":
        return cls(
            id=row[0],
            customer_id=row[1],
            branch_id=row[2],
            account_id=row[3],
            loan_type=row[4],
            principal=Decimal(str(row[5])),
            interest_rate=Decimal(str(row[6])),
            tenure_months=row[7],
            emi=Decimal(str(row[8])),
            outstanding=Decimal(str(row[9])),
            status=row[10],
            created_at=row[11],
            approved_at=row[12],
            disbursed_at=row[13],
        )


class LoanProduct(ABC):
    """Base loan product — subclasses define rate limits and EMI rules."""

    loan_type: ClassVar[str]
    default_rate: ClassVar[Decimal]

    @classmethod
    @abstractmethod
    def max_tenure_months(cls) -> int:
        pass

    @classmethod
    @abstractmethod
    def min_principal(cls) -> Decimal:
        pass

    @classmethod
    @abstractmethod
    def max_principal(cls) -> Decimal:
        pass

    @classmethod
    def calculate_emi(
        cls, principal: Decimal, annual_rate: Decimal, tenure_months: int
    ) -> Decimal:
        if tenure_months <= 0:
            raise ValueError("Tenure must be at least 1 month.")

        monthly_rate = annual_rate / Decimal("1200")
        if monthly_rate == 0:
            emi = principal / Decimal(tenure_months)
        else:
            factor = (1 + monthly_rate) ** tenure_months
            emi = principal * monthly_rate * factor / (factor - 1)

        return emi.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    @classmethod
    def validate_application(
        cls, principal: Decimal, tenure_months: int
    ) -> None:
        if principal < cls.min_principal():
            raise ValueError(
                f"{cls.loan_type} loan minimum principal is Rs.{cls.min_principal():.2f}."
            )
        if principal > cls.max_principal():
            raise ValueError(
                f"{cls.loan_type} loan maximum principal is Rs.{cls.max_principal():.2f}."
            )
        if tenure_months > cls.max_tenure_months():
            raise ValueError(
                f"{cls.loan_type} loan maximum tenure is {cls.max_tenure_months()} months."
            )


class PersonalLoan(LoanProduct):
    loan_type = "PERSONAL"
    default_rate = Decimal("12.00")

    @classmethod
    def max_tenure_months(cls) -> int:
        return 60

    @classmethod
    def min_principal(cls) -> Decimal:
        return Decimal("10000.00")

    @classmethod
    def max_principal(cls) -> Decimal:
        return Decimal("500000.00")


class HomeLoan(LoanProduct):
    loan_type = "HOME"
    default_rate = Decimal("8.50")

    @classmethod
    def max_tenure_months(cls) -> int:
        return 360

    @classmethod
    def min_principal(cls) -> Decimal:
        return Decimal("100000.00")

    @classmethod
    def max_principal(cls) -> Decimal:
        return Decimal("5000000.00")


class AutoLoan(LoanProduct):
    loan_type = "AUTO"
    default_rate = Decimal("10.00")

    @classmethod
    def max_tenure_months(cls) -> int:
        return 84

    @classmethod
    def min_principal(cls) -> Decimal:
        return Decimal("50000.00")

    @classmethod
    def max_principal(cls) -> Decimal:
        return Decimal("2000000.00")


LOAN_PRODUCTS: dict[str, type[LoanProduct]] = {
    "PERSONAL": PersonalLoan,
    "HOME": HomeLoan,
    "AUTO": AutoLoan,
}


def get_loan_product(loan_type: str) -> LoanProduct:
    product = LOAN_PRODUCTS.get(loan_type.upper())
    if product is None:
        valid = ", ".join(sorted(LOAN_PRODUCTS))
        raise ValueError(f"Invalid loan type '{loan_type}'. Choose from: {valid}.")
    return product
