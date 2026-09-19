from typing import List, Optional

from database.connection import get_cursor
from models.customer import Customer


class CustomerRepository:
    def create(
        self,
        branch_id: int,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
    ) -> Customer:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                INSERT INTO customers (branch_id, first_name, last_name, email, phone)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, branch_id, first_name, last_name, email, phone, created_at
                """,
                (branch_id, first_name, last_name, email, phone),
            )
            return Customer.from_row(cur.fetchone())

    def get_by_id(self, customer_id: int) -> Optional[Customer]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, branch_id, first_name, last_name, email, phone, created_at
                FROM customers
                WHERE id = %s
                """,
                (customer_id,),
            )
            row = cur.fetchone()
            return Customer.from_row(row) if row else None

    def get_by_email(self, email: str) -> Optional[Customer]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, branch_id, first_name, last_name, email, phone, created_at
                FROM customers
                WHERE email = %s
                """,
                (email,),
            )
            row = cur.fetchone()
            return Customer.from_row(row) if row else None

    def list_all(self) -> List[Customer]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, branch_id, first_name, last_name, email, phone, created_at
                FROM customers
                ORDER BY id
                """
            )
            return [Customer.from_row(row) for row in cur.fetchall()]

    def list_by_branch(self, branch_id: int) -> List[Customer]:
        with get_cursor() as (_, cur):
            cur.execute(
                """
                SELECT id, branch_id, first_name, last_name, email, phone, created_at
                FROM customers
                WHERE branch_id = %s
                ORDER BY id
                """,
                (branch_id,),
            )
            return [Customer.from_row(row) for row in cur.fetchall()]
