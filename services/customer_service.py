from typing import List

from models.customer import Customer
from repositories.branch_repository import BranchRepository
from repositories.customer_repository import CustomerRepository
from utils.validators import (
    validate_email,
    validate_phone,
    validate_positive_id,
    validate_required_string,
)


class CustomerService:
    def __init__(
        self,
        customer_repository: CustomerRepository | None = None,
        branch_repository: BranchRepository | None = None,
    ) -> None:
        self.customer_repository = customer_repository or CustomerRepository()
        self.branch_repository = branch_repository or BranchRepository()

    def register_customer(
        self,
        branch_id: int,
        first_name: str,
        last_name: str,
        email: str,
        phone: str,
    ) -> Customer:
        branch_id = validate_positive_id(branch_id, "Branch ID")
        first_name = validate_required_string(first_name, "First name")
        last_name = validate_required_string(last_name, "Last name")
        email = validate_email(email)
        phone = validate_phone(phone)

        if self.branch_repository.get_by_id(branch_id) is None:
            raise ValueError(f"Branch with ID {branch_id} not found.")

        if self.customer_repository.get_by_email(email):
            raise ValueError(f"A customer with email '{email}' already exists.")

        return self.customer_repository.create(
            branch_id, first_name, last_name, email, phone
        )

    def list_customers(self) -> List[Customer]:
        return self.customer_repository.list_all()

    def list_customers_by_branch(self, branch_id: int) -> List[Customer]:
        branch_id = validate_positive_id(branch_id, "Branch ID")
        if self.branch_repository.get_by_id(branch_id) is None:
            raise ValueError(f"Branch with ID {branch_id} not found.")
        return self.customer_repository.list_by_branch(branch_id)

    def get_customer(self, customer_id: int) -> Customer:
        customer_id = validate_positive_id(customer_id, "Customer ID")
        customer = self.customer_repository.get_by_id(customer_id)
        if customer is None:
            raise ValueError(f"Customer with ID {customer_id} not found.")
        return customer
