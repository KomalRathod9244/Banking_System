from typing import List, Optional

from database.connection import get_cursor
from models.bank import Bank


class BankRepository:
    def create(self, name: str, code: str) -> Bank:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                INSERT INTO banks (name, code)
                VALUES (%s, %s)
                RETURNING id, name, code, created_at
                """,
                (name, code),
            )
            return Bank.from_row(cur.fetchone())

    def get_by_id(self, bank_id: int) -> Optional[Bank]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, name, code, created_at
                FROM banks
                WHERE id = %s
                """,
                (bank_id,),
            )
            row = cur.fetchone()
            return Bank.from_row(row) if row else None

    def get_by_code(self, code: str) -> Optional[Bank]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, name, code, created_at
                FROM banks
                WHERE code = %s
                """,
                (code,),
            )
            row = cur.fetchone()
            return Bank.from_row(row) if row else None

    def list_all(self) -> List[Bank]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, name, code, created_at
                FROM banks
                ORDER BY id
                """
            )
            return [Bank.from_row(row) for row in cur.fetchall()]
