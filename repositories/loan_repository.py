from decimal import Decimal
from typing import List, Optional

from database.connection import get_cursor
from models.loan import Loan
from models.loan_payment import LoanPayment

_LOAN_COLUMNS = """
    id, customer_id, branch_id, account_id, loan_type,
    principal, interest_rate, tenure_months, emi, outstanding,
    status, created_at, approved_at, disbursed_at
"""


class LoanRepository:
    def create(
        self,
        customer_id: int,
        branch_id: int,
        loan_type: str,
        principal: Decimal,
        interest_rate: Decimal,
        tenure_months: int,
        emi: Decimal,
    ) -> Loan:
        with get_cursor() as (_, cur):
            cur.execute(
                f"""
                INSERT INTO loans (
                    customer_id, branch_id, loan_type, principal,
                    interest_rate, tenure_months, emi, outstanding, status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'PENDING')
                RETURNING {_LOAN_COLUMNS}
                """,
                (
                    customer_id,
                    branch_id,
                    loan_type,
                    principal,
                    interest_rate,
                    tenure_months,
                    emi,
                    principal,
                ),
            )
            return Loan.from_row(cur.fetchone())

    def get_by_id(self, loan_id: int) -> Optional[Loan]:
        with get_cursor() as (_, cur):
            cur.execute(
                f"SELECT {_LOAN_COLUMNS} FROM loans WHERE id = %s",
                (loan_id,),
            )
            row = cur.fetchone()
            return Loan.from_row(row) if row else None

    def list_all(self) -> List[Loan]:
        with get_cursor() as (_, cur):
            cur.execute(
                f"SELECT {_LOAN_COLUMNS} FROM loans ORDER BY id"
            )
            return [Loan.from_row(row) for row in cur.fetchall()]

    def list_by_customer(self, customer_id: int) -> List[Loan]:
        with get_cursor() as (_, cur):
            cur.execute(
                f"""
                SELECT {_LOAN_COLUMNS}
                FROM loans
                WHERE customer_id = %s
                ORDER BY id
                """,
                (customer_id,),
            )
            return [Loan.from_row(row) for row in cur.fetchall()]

    def update_status(self, loan_id: int, status: str) -> Loan:
        with get_cursor() as (_, cur):
            approved_clause = (
                ", approved_at = CURRENT_TIMESTAMP" if status == "APPROVED" else ""
            )
            cur.execute(
                f"""
                UPDATE loans
                SET status = %s{approved_clause}
                WHERE id = %s
                RETURNING {_LOAN_COLUMNS}
                """,
                (status, loan_id),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError(f"Loan with ID {loan_id} not found.")
            return Loan.from_row(row)

    def disburse(self, loan_id: int, account_id: int) -> Loan:
        with get_cursor() as (_, cur):
            cur.execute(
                f"SELECT {_LOAN_COLUMNS} FROM loans WHERE id = %s FOR UPDATE",
                (loan_id,),
            )
            loan_row = cur.fetchone()
            if loan_row is None:
                raise ValueError(f"Loan with ID {loan_id} not found.")

            loan = Loan.from_row(loan_row)
            if loan.status != "APPROVED":
                raise ValueError(
                    f"Loan {loan_id} cannot be disbursed (status: {loan.status}). "
                    "Only APPROVED loans can be disbursed."
                )

            cur.execute(
                """
                SELECT id, customer_id, branch_id, account_number,
                       account_type, balance, status, created_at
                FROM accounts
                WHERE id = %s
                FOR UPDATE
                """,
                (account_id,),
            )
            account_row = cur.fetchone()
            if account_row is None:
                raise ValueError(f"Account with ID {account_id} not found.")

            if account_row[1] != loan.customer_id:
                raise ValueError(
                    f"Account does not belong to loan customer {loan.customer_id}."
                )
            if account_row[6] != "ACTIVE":
                raise ValueError(
                    f"Account '{account_row[3]}' is not active (status: {account_row[6]})."
                )

            new_balance = Decimal(str(account_row[5])) + loan.principal
            cur.execute(
                "UPDATE accounts SET balance = %s WHERE id = %s",
                (new_balance, account_id),
            )
            cur.execute(
                """
                INSERT INTO transactions (
                    account_id, transaction_type, amount, balance_after, description
                )
                VALUES (%s, 'DEPOSIT', %s, %s, %s)
                """,
                (
                    account_id,
                    loan.principal,
                    new_balance,
                    f"Loan disbursement - Loan #{loan_id} ({loan.loan_type})",
                ),
            )
            cur.execute(
                f"""
                UPDATE loans
                SET status = 'ACTIVE',
                    account_id = %s,
                    disbursed_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING {_LOAN_COLUMNS}
                """,
                (account_id, loan_id),
            )
            return Loan.from_row(cur.fetchone())

    def repay(self, loan_id: int, amount: Decimal) -> tuple[Loan, LoanPayment]:
        with get_cursor() as (_, cur):
            cur.execute(
                f"SELECT {_LOAN_COLUMNS} FROM loans WHERE id = %s FOR UPDATE",
                (loan_id,),
            )
            loan_row = cur.fetchone()
            if loan_row is None:
                raise ValueError(f"Loan with ID {loan_id} not found.")

            loan = Loan.from_row(loan_row)
            if loan.status != "ACTIVE":
                raise ValueError(
                    f"Loan {loan_id} is not active (status: {loan.status})."
                )
            if loan.account_id is None:
                raise ValueError(f"Loan {loan_id} has no linked disbursement account.")
            if amount > loan.outstanding:
                raise ValueError(
                    f"Repayment exceeds outstanding balance. "
                    f"Outstanding: Rs.{loan.outstanding:.2f}, requested: Rs.{amount:.2f}."
                )

            cur.execute(
                """
                SELECT id, customer_id, branch_id, account_number,
                       account_type, balance, status, created_at
                FROM accounts
                WHERE id = %s
                FOR UPDATE
                """,
                (loan.account_id,),
            )
            account_row = cur.fetchone()
            if account_row is None:
                raise ValueError(f"Linked account for loan {loan_id} not found.")

            account_balance = Decimal(str(account_row[5]))
            if account_balance < amount:
                raise ValueError(
                    f"Insufficient funds in account '{account_row[3]}'. "
                    f"Available: Rs.{account_balance:.2f}, required: Rs.{amount:.2f}."
                )

            new_account_balance = account_balance - amount
            cur.execute(
                "UPDATE accounts SET balance = %s WHERE id = %s",
                (new_account_balance, loan.account_id),
            )
            cur.execute(
                """
                INSERT INTO transactions (
                    account_id, transaction_type, amount, balance_after, description
                )
                VALUES (%s, 'WITHDRAWAL', %s, %s, %s)
                """,
                (
                    loan.account_id,
                    amount,
                    new_account_balance,
                    f"Loan repayment - Loan #{loan_id}",
                ),
            )

            new_outstanding = loan.outstanding - amount
            new_status = "CLOSED" if new_outstanding == Decimal("0.00") else "ACTIVE"

            cur.execute(
                f"""
                UPDATE loans
                SET outstanding = %s, status = %s
                WHERE id = %s
                RETURNING {_LOAN_COLUMNS}
                """,
                (new_outstanding, new_status, loan_id),
            )
            updated_loan = Loan.from_row(cur.fetchone())

            cur.execute(
                """
                INSERT INTO loan_payments (loan_id, amount, outstanding_after)
                VALUES (%s, %s, %s)
                RETURNING id, loan_id, amount, outstanding_after, created_at
                """,
                (loan_id, amount, new_outstanding),
            )
            payment = LoanPayment.from_row(cur.fetchone())
            return updated_loan, payment
