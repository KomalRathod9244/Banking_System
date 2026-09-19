import random
from decimal import Decimal
from typing import List, Optional

from database.connection import get_cursor
from models.account import Account


class AccountRepository:
    def _generate_account_number(self, branch_id: int) -> str:
        suffix = random.randint(100000, 999999)
        return f"ACC{branch_id:03d}{suffix}"

    def create(
        self,
        customer_id: int,
        branch_id: int,
        account_type: str = "SAVINGS",
        initial_balance: Decimal = Decimal("0.00"),
    ) -> Account:
        with get_cursor() as (_, cur):
            for _ in range(10):
                account_number = self._generate_account_number(branch_id)
                cur.execute(
                    "SELECT 1 FROM accounts WHERE account_number = %s",
                    (account_number,),
                )
                if cur.fetchone() is None:
                    break
            else:
                raise RuntimeError("Unable to generate a unique account number.")

            cur.execute(
                """
                INSERT INTO accounts (
                    customer_id, branch_id, account_number, account_type, balance
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, customer_id, branch_id, account_number,
                          account_type, balance, status, created_at
                """,
                (customer_id, branch_id, account_number, account_type, initial_balance),
            )
            return Account.from_row(cur.fetchone())

    def get_by_id(self, account_id: int) -> Optional[Account]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, customer_id, branch_id, account_number,
                       account_type, balance, status, created_at
                FROM accounts
                WHERE id = %s
                """,
                (account_id,),
            )
            row = cur.fetchone()
            return Account.from_row(row) if row else None

    def get_by_account_number(self, account_number: str) -> Optional[Account]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, customer_id, branch_id, account_number,
                       account_type, balance, status, created_at
                FROM accounts
                WHERE account_number = %s
                """,
                (account_number,),
            )
            row = cur.fetchone()
            return Account.from_row(row) if row else None

    def update_balance(self, account_id: int, new_balance: Decimal) -> Account:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                UPDATE accounts
                SET balance = %s
                WHERE id = %s
                RETURNING id, customer_id, branch_id, account_number,
                          account_type, balance, status, created_at
                """,
                (new_balance, account_id),
            )
            row = cur.fetchone()
            if row is None:
                raise ValueError(f"Account with ID {account_id} not found.")
            return Account.from_row(row)

    def apply_transaction(
        self,
        account_id: int,
        transaction_type: str,
        amount: Decimal,
        description: str | None = None,
    ) -> tuple[Account, "Transaction"]:
        from models.transaction import Transaction

        with get_cursor() as (_, cur):
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
            row = cur.fetchone()
            if row is None:
                raise ValueError(f"Account with ID {account_id} not found.")

            account = Account.from_row(row)
            if account.status != "ACTIVE":
                raise ValueError(
                    f"Account '{account.account_number}' is not active "
                    f"(status: {account.status})."
                )

            if transaction_type == "WITHDRAWAL" and account.balance < amount:
                raise ValueError(
                    f"Insufficient funds. Available balance: ${account.balance:.2f}, "
                    f"requested: ${amount:.2f}."
                )

            if transaction_type == "DEPOSIT":
                new_balance = account.balance + amount
            elif transaction_type == "WITHDRAWAL":
                new_balance = account.balance - amount
            else:
                raise ValueError(f"Unsupported transaction type: {transaction_type}")

            cur.execute(
                """
                UPDATE accounts
                SET balance = %s
                WHERE id = %s
                RETURNING id, customer_id, branch_id, account_number,
                          account_type, balance, status, created_at
                """,
                (new_balance, account_id),
            )
            updated_account = Account.from_row(cur.fetchone())

            cur.execute(
                """
                INSERT INTO transactions (
                    account_id, transaction_type, amount, balance_after, description
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, account_id, transaction_type, amount,
                          balance_after, description, created_at
                """,
                (account_id, transaction_type, amount, new_balance, description),
            )
            transaction = Transaction.from_row(cur.fetchone())
            return updated_account, transaction

    def list_all(self) -> List[Account]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, customer_id, branch_id, account_number,
                       account_type, balance, status, created_at
                FROM accounts
                ORDER BY id
                """
            )
            return [Account.from_row(row) for row in cur.fetchall()]

    def list_by_customer(self, customer_id: int) -> List[Account]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, customer_id, branch_id, account_number,
                       account_type, balance, status, created_at
                FROM accounts
                WHERE customer_id = %s
                ORDER BY id
                """,
                (customer_id,),
            )
            return [Account.from_row(row) for row in cur.fetchall()]
