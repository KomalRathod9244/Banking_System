from decimal import Decimal
from typing import List, Optional

from models.loan import Loan, get_loan_product
from models.loan_payment import LoanPayment
from repositories.account_repository import AccountRepository
from repositories.branch_repository import BranchRepository
from repositories.customer_repository import CustomerRepository
from repositories.loan_payment_repository import LoanPaymentRepository
from repositories.loan_repository import LoanRepository
from utils.validators import validate_amount, validate_positive_id, validate_required_string


class LoanService:
    def __init__(
        self,
        loan_repository: LoanRepository | None = None,
        loan_payment_repository: LoanPaymentRepository | None = None,
        customer_repository: CustomerRepository | None = None,
        branch_repository: BranchRepository | None = None,
        account_repository: AccountRepository | None = None,
    ) -> None:
        self.loan_repository = loan_repository or LoanRepository()
        self.loan_payment_repository = loan_payment_repository or LoanPaymentRepository()
        self.customer_repository = customer_repository or CustomerRepository()
        self.branch_repository = branch_repository or BranchRepository()
        self.account_repository = account_repository or AccountRepository()

    def apply_for_loan(
        self,
        customer_id: int,
        branch_id: int,
        loan_type: str,
        principal: Decimal,
        tenure_months: int,
    ) -> Loan:
        customer_id = validate_positive_id(customer_id, "Customer ID")
        branch_id = validate_positive_id(branch_id, "Branch ID")
        loan_type = validate_required_string(loan_type, "Loan type").upper()
        principal = validate_amount(principal)
        tenure_months = validate_positive_id(tenure_months, "Tenure (months)")

        product = get_loan_product(loan_type)
        product.validate_application(principal, tenure_months)

        customer = self.customer_repository.get_by_id(customer_id)
        if customer is None:
            raise ValueError(f"Customer with ID {customer_id} not found.")

        branch = self.branch_repository.get_by_id(branch_id)
        if branch is None:
            raise ValueError(f"Branch with ID {branch_id} not found.")

        if customer.branch_id != branch_id:
            raise ValueError(
                f"Customer {customer_id} is registered at branch {customer.branch_id}, "
                f"not branch {branch_id}."
            )

        emi = product.calculate_emi(principal, product.default_rate, tenure_months)

        return self.loan_repository.create(
            customer_id,
            branch_id,
            loan_type,
            principal,
            product.default_rate,
            tenure_months,
            emi,
        )

    def approve_loan(self, loan_id: int) -> Loan:
        loan = self._get_loan(loan_id)
        if loan.status != "PENDING":
            raise ValueError(
                f"Loan {loan_id} cannot be approved (status: {loan.status})."
            )
        return self.loan_repository.update_status(loan_id, "APPROVED")

    def reject_loan(self, loan_id: int) -> Loan:
        loan = self._get_loan(loan_id)
        if loan.status != "PENDING":
            raise ValueError(
                f"Loan {loan_id} cannot be rejected (status: {loan.status})."
            )
        return self.loan_repository.update_status(loan_id, "REJECTED")

    def disburse_loan(self, loan_id: int, account_number: str) -> Loan:
        loan_id = validate_positive_id(loan_id, "Loan ID")
        account_number = validate_required_string(account_number, "Account number")

        loan = self._get_loan(loan_id)
        account = self.account_repository.get_by_account_number(account_number)
        if account is None:
            raise ValueError(f"Account '{account_number}' not found.")

        return self.loan_repository.disburse(loan_id, account.id)

    def repay_loan(self, loan_id: int, amount: Decimal) -> tuple[Loan, LoanPayment]:
        loan_id = validate_positive_id(loan_id, "Loan ID")
        amount = validate_amount(amount)
        return self.loan_repository.repay(loan_id, amount)

    def get_loan(self, loan_id: int) -> Loan:
        return self._get_loan(loan_id)

    def list_loans(self) -> List[Loan]:
        return self.loan_repository.list_all()

    def list_loans_by_customer(self, customer_id: int) -> List[Loan]:
        customer_id = validate_positive_id(customer_id, "Customer ID")
        if self.customer_repository.get_by_id(customer_id) is None:
            raise ValueError(f"Customer with ID {customer_id} not found.")
        return self.loan_repository.list_by_customer(customer_id)

    def get_payment_history(
        self, loan_id: int, limit: int = 20
    ) -> List[LoanPayment]:
        self._get_loan(loan_id)
        limit = validate_positive_id(limit, "Limit")
        return self.loan_payment_repository.list_by_loan(loan_id, limit=limit)

    def preview_emi(
        self,
        loan_type: str,
        principal: Decimal,
        tenure_months: int,
        interest_rate: Optional[Decimal] = None,
    ) -> Decimal:
        loan_type = validate_required_string(loan_type, "Loan type").upper()
        principal = validate_amount(principal)
        tenure_months = validate_positive_id(tenure_months, "Tenure (months)")

        product = get_loan_product(loan_type)
        product.validate_application(principal, tenure_months)
        rate = interest_rate if interest_rate is not None else product.default_rate
        return product.calculate_emi(principal, rate, tenure_months)

    def _get_loan(self, loan_id: int) -> Loan:
        loan_id = validate_positive_id(loan_id, "Loan ID")
        loan = self.loan_repository.get_by_id(loan_id)
        if loan is None:
            raise ValueError(f"Loan with ID {loan_id} not found.")
        return loan
