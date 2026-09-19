from decimal import Decimal
from typing import List, Optional

from models.account import Account
from models.transaction import Transaction
from repositories.account_repository import AccountRepository
from repositories.branch_repository import BranchRepository
from repositories.customer_repository import CustomerRepository
from repositories.transaction_repository import TransactionRepository
from utils.validators import validate_amount, validate_positive_id, validate_required_string


class AccountService:
    VALID_ACCOUNT_TYPES = {"SAVINGS", "CHECKING"}

    def __init__(
        self,
        account_repository: AccountRepository | None = None,
        customer_repository: CustomerRepository | None = None,
        branch_repository: BranchRepository | None = None,
        transaction_repository: TransactionRepository | None = None,
    ) -> None:
        self.account_repository = account_repository or AccountRepository()
        self.customer_repository = customer_repository or CustomerRepository()
        self.branch_repository = branch_repository or BranchRepository()
        self.transaction_repository = transaction_repository or TransactionRepository()

    def open_account(
        self,
        customer_id: int,
        branch_id: int,
        account_type: str = "SAVINGS",
        initial_deposit: Decimal = Decimal("0.00"),
    ) -> Account:
        customer_id = validate_positive_id(customer_id, "Customer ID")
        branch_id = validate_positive_id(branch_id, "Branch ID")
        account_type = validate_required_string(account_type, "Account type").upper()
        initial_deposit = validate_amount(initial_deposit, allow_zero=True)

        if account_type not in self.VALID_ACCOUNT_TYPES:
            raise ValueError(
                f"Invalid account type '{account_type}'. "
                f"Choose from: {', '.join(sorted(self.VALID_ACCOUNT_TYPES))}."
            )

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

        account = self.account_repository.create(
            customer_id, branch_id, account_type, initial_deposit
        )

        if initial_deposit > Decimal("0.00"):
            self.transaction_repository.create(
                account.id,
                "DEPOSIT",
                initial_deposit,
                initial_deposit,
                "Initial deposit",
            )

        return account

    def deposit(
        self,
        account_number: str,
        amount: Decimal,
        description: Optional[str] = None,
    ) -> Transaction:
        account_number = validate_required_string(account_number, "Account number")
        amount = validate_amount(amount)

        account = self._get_active_account(account_number)
        _, transaction = self.account_repository.apply_transaction(
            account.id,
            "DEPOSIT",
            amount,
            description or "Deposit",
        )
        return transaction

    def withdraw(
        self,
        account_number: str,
        amount: Decimal,
        description: Optional[str] = None,
    ) -> Transaction:
        account_number = validate_required_string(account_number, "Account number")
        amount = validate_amount(amount)

        account = self._get_active_account(account_number)
        _, transaction = self.account_repository.apply_transaction(
            account.id,
            "WITHDRAWAL",
            amount,
            description or "Withdrawal",
        )
        return transaction

    def check_balance(self, account_number: str) -> Decimal:
        account_number = validate_required_string(account_number, "Account number")
        account = self._get_active_account(account_number)
        return account.balance

    def get_account(self, account_number: str) -> Account:
        account_number = validate_required_string(account_number, "Account number")
        return self._get_active_account(account_number)

    def list_accounts(self) -> List[Account]:
        return self.account_repository.list_all()

    def _get_active_account(self, account_number: str) -> Account:
        account = self.account_repository.get_by_account_number(account_number)
        if account is None:
            raise ValueError(f"Account '{account_number}' not found.")

        if account.status != "ACTIVE":
            raise ValueError(
                f"Account '{account_number}' is not active (status: {account.status})."
            )

        return account
