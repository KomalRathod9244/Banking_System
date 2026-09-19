import re
from decimal import Decimal, InvalidOperation
from typing import Union


def validate_email(email: str) -> str:
    email = email.strip()
    if not email:
        raise ValueError("Email is required.")

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        raise ValueError(f"Invalid email format: '{email}'.")

    return email.lower()


def validate_phone(phone: str) -> str:
    phone = phone.strip()
    if not phone:
        raise ValueError("Phone number is required.")

    digits = re.sub(r"\D", "", phone)
    if len(digits) < 10 or len(digits) > 15:
        raise ValueError(
            f"Invalid phone number '{phone}'. Must contain 10-15 digits."
        )

    return phone


def validate_amount(
    amount: Union[str, Decimal, float, int],
    allow_zero: bool = False,
) -> Decimal:
    try:
        if isinstance(amount, str):
            amount = amount.strip()
            if not amount:
                raise ValueError("Amount is required.")
            value = Decimal(amount)
        else:
            value = Decimal(str(amount))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid amount: '{amount}'.") from exc

    if value < Decimal("0.00"):
        raise ValueError("Amount cannot be negative.")

    if not allow_zero and value == Decimal("0.00"):
        raise ValueError("Amount must be greater than zero.")

    if value.as_tuple().exponent < -2:
        raise ValueError("Amount cannot have more than 2 decimal places.")

    return value.quantize(Decimal("0.01"))


def validate_positive_id(value: Union[str, int], field_name: str = "ID") -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a positive integer.") from exc

    if parsed <= 0:
        raise ValueError(f"{field_name} must be a positive integer.")

    return parsed


def validate_required_string(value: str, field_name: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError(f"{field_name} is required.")
    return value
