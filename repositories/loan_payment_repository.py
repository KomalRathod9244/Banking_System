from typing import List, Optional

from database.connection import get_cursor
from models.loan_payment import LoanPayment


class LoanPaymentRepository:
    def get_by_id(self, payment_id: int) -> Optional[LoanPayment]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, loan_id, amount, outstanding_after, created_at
                FROM loan_payments
                WHERE id = %s
                """,
                (payment_id,),
            )
            row = cur.fetchone()
            return LoanPayment.from_row(row) if row else None

    def list_by_loan(self, loan_id: int, limit: int | None = None) -> List[LoanPayment]:
        with get_cursor() as (_, cur):
            query = """
                SELECT id, loan_id, amount, outstanding_after, created_at
                FROM loan_payments
                WHERE loan_id = %s
                ORDER BY created_at DESC
            """
            if limit is not None:
                query += " LIMIT %s"
                cur.execute(query, (loan_id, limit))
            else:
                cur.execute(query, (loan_id,))
            return [LoanPayment.from_row(row) for row in cur.fetchall()]
