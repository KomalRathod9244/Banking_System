from decimal import Decimal
from typing import List, Optional

from database.connection import get_cursor
from models.transaction import Transaction


class TransactionRepository:
    def create(
        self,
        account_id: int,
        transaction_type: str,
        amount: Decimal,
        balance_after: Decimal,
        description: Optional[str] = None,
    ) -> Transaction:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                INSERT INTO transactions (
                    account_id, transaction_type, amount, balance_after, description
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, account_id, transaction_type, amount,
                          balance_after, description, created_at
                """,
                (account_id, transaction_type, amount, balance_after, description),
            )
            return Transaction.from_row(cur.fetchone())

    def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, account_id, transaction_type, amount,
                       balance_after, description, created_at
                FROM transactions
                WHERE id = %s
                """,
                (transaction_id,),
            )
            row = cur.fetchone()
            return Transaction.from_row(row) if row else None

    def list_by_account(self, account_id: int) -> List[Transaction]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, account_id, transaction_type, amount,
                       balance_after, description, created_at
                FROM transactions
                WHERE account_id = %s
                ORDER BY created_at DESC
                """,
                (account_id,),
            )
            return [Transaction.from_row(row) for row in cur.fetchall()]
