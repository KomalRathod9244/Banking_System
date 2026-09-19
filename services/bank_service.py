from typing import List

from models.bank import Bank
from repositories.bank_repository import BankRepository
from utils.validators import validate_positive_id, validate_required_string


class BankService:
    def __init__(self, repository: BankRepository | None = None) -> None:
        self.repository = repository or BankRepository()

    def create_bank(self, name: str, code: str) -> Bank:
        name = validate_required_string(name, "Bank name")
        code = validate_required_string(code, "Bank code").upper()

        if self.repository.get_by_code(code):
            raise ValueError(f"A bank with code '{code}' already exists.")

        return self.repository.create(name, code)

    def list_banks(self) -> List[Bank]:
        return self.repository.list_all()

    def get_bank(self, bank_id: int) -> Bank:
        bank_id = validate_positive_id(bank_id, "Bank ID")
        bank = self.repository.get_by_id(bank_id)
        if bank is None:
            raise ValueError(f"Bank with ID {bank_id} not found.")
        return bank
