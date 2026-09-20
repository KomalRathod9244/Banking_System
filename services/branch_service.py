from typing import List, Optional

from models.branch import Branch
from repositories.bank_repository import BankRepository
from repositories.branch_repository import BranchRepository
from utils.validators import validate_phone, validate_positive_id, validate_required_string


class BranchService:
    def __init__(
        self,
        branch_repository: BranchRepository | None = None,
        bank_repository: BankRepository | None = None,
    ) -> None:
        self.branch_repository = branch_repository or BranchRepository()
        self.bank_repository = bank_repository or BankRepository()

    def add_branch(
        self,
        bank_id: int,
        name: str,
        address: Optional[str] = None,
        phone: Optional[str] = None,
    ) -> Branch:
        bank_id = validate_positive_id(bank_id, "Bank ID")
        name = validate_required_string(name, "Branch name")

        if self.bank_repository.get_by_id(bank_id) is None:
            raise ValueError(f"Bank with ID {bank_id} not found.")

        if phone:
            phone = validate_phone(phone)

        return self.branch_repository.create(bank_id, name, address, phone)

    def list_branches(self) -> List[Branch]:
        return self.branch_repository.list_all()

    def list_branches_by_bank(self, bank_id: int) -> List[Branch]:
        bank_id = validate_positive_id(bank_id, "Bank ID")
        if self.bank_repository.get_by_id(bank_id) is None:
            raise ValueError(f"Bank with ID {bank_id} not found.")
        return self.branch_repository.list_by_bank(bank_id)

    def get_branch(self, branch_id: int) -> Branch:
        branch_id = validate_positive_id(branch_id, "Branch ID")
        branch = self.branch_repository.get_by_id(branch_id)
        if branch is None:
            raise ValueError(f"Branch with ID {branch_id} not found.")
        return branch
