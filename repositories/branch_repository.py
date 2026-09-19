from typing import List, Optional

from database.connection import get_cursor
from models.branch import Branch


class BranchRepository:
    def create(
        self,
        bank_id: int,
        name: str,
        address: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> Branch:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                INSERT INTO branches (bank_id, name, address, phone)
                VALUES (%s, %s, %s, %s)
                RETURNING id, bank_id, name, address, phone, created_at
                """,
                (bank_id, name, address, phone),
            )
            return Branch.from_row(cur.fetchone())

    def get_by_id(self, branch_id: int) -> Optional[Branch]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, bank_id, name, address, phone, created_at
                FROM branches
                WHERE id = %s
                """,
                (branch_id,),
            )
            row = cur.fetchone()
            return Branch.from_row(row) if row else None

    def list_all(self) -> List[Branch]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, bank_id, name, address, phone, created_at
                FROM branches
                ORDER BY id
                """
            )
            return [Branch.from_row(row) for row in cur.fetchall()]

    def list_by_bank(self, bank_id: int) -> List[Branch]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, bank_id, name, address, phone, created_at
                FROM branches
                WHERE bank_id = %s
                ORDER BY id
                """,
                (bank_id,),
            )
            return [Branch.from_row(row) for row in cur.fetchall()]
