#!/usr/bin/env python3
"""Phase 1 Banking System - Terminal CLI."""

import sys
from decimal import Decimal

from services.account_service import AccountService
from services.bank_service import BankService
from services.branch_service import BranchService
from services.customer_service import CustomerService


def print_header(title: str) -> None:
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)


def print_success(message: str) -> None:
    print(f"\n[SUCCESS] {message}")


def print_error(message: str) -> None:
    print(f"\n[ERROR] {message}")


def prompt(message: str, default: str = "") -> str:
    if default:
        value = input(f"{message} [{default}]: ").strip()
        return value or default
    return input(f"{message}: ").strip()


def pause() -> None:
    input("\nPress Enter to continue...")


def handle_create_bank(bank_service: BankService) -> None:
    print_header("Create Bank")
    name = prompt("Bank name")
    code = prompt("Bank code")
    try:
        bank = bank_service.create_bank(name, code)
        print_success(f"Bank created: {bank.name} (ID: {bank.id}, Code: {bank.code})")
    except ValueError as exc:
        print_error(str(exc))


def handle_list_banks(bank_service: BankService) -> None:
    print_header("List Banks")
    try:
        banks = bank_service.list_banks()
        if not banks:
            print("No banks found.")
            return
        print(f"{'ID':<6}{'Code':<12}{'Name':<30}{'Created At'}")
        print("-" * 70)
        for bank in banks:
            print(f"{bank.id:<6}{bank.code:<12}{bank.name:<30}{bank.created_at}")
    except ValueError as exc:
        print_error(str(exc))


def handle_add_branch(branch_service: BranchService) -> None:
    print_header("Add Branch")
    bank_id = prompt("Bank ID")
    name = prompt("Branch name")
    address = prompt("Address (optional)", "")
    phone = prompt("Phone (optional)", "")
    try:
        branch = branch_service.add_branch(
            int(bank_id),
            name,
            address or None,
            phone or None,
        )
        print_success(
            f"Branch created: {branch.name} (ID: {branch.id}, Bank ID: {branch.bank_id})"
        )
    except ValueError as exc:
        print_error(str(exc))


def handle_list_branches(branch_service: BranchService) -> None:
    print_header("List Branches")
    try:
        branches = branch_service.list_branches()
        if not branches:
            print("No branches found.")
            return
        print(f"{'ID':<6}{'Bank ID':<10}{'Name':<25}{'Phone':<16}{'Address'}")
        print("-" * 90)
        for branch in branches:
            address = branch.address or "-"
            phone = branch.phone or "-"
            print(
                f"{branch.id:<6}{branch.bank_id:<10}{branch.name:<25}"
                f"{phone:<16}{address}"
            )
    except ValueError as exc:
        print_error(str(exc))


def handle_register_customer(customer_service: CustomerService) -> None:
    print_header("Register Customer")
    branch_id = prompt("Branch ID")
    first_name = prompt("First name")
    last_name = prompt("Last name")
    email = prompt("Email")
    phone = prompt("Phone")
    try:
        customer = customer_service.register_customer(
            int(branch_id),
            first_name,
            last_name,
            email,
            phone,
        )
        print_success(
            f"Customer registered: {customer.full_name} "
            f"(ID: {customer.id}, Branch ID: {customer.branch_id})"
        )
    except ValueError as exc:
        print_error(str(exc))


def handle_list_customers(customer_service: CustomerService) -> None:
    print_header("List Customers")
    try:
        customers = customer_service.list_customers()
        if not customers:
            print("No customers found.")
            return
        print(f"{'ID':<6}{'Branch':<8}{'Name':<25}{'Email':<28}{'Phone'}")
        print("-" * 90)
        for customer in customers:
            print(
                f"{customer.id:<6}{customer.branch_id:<8}{customer.full_name:<25}"
                f"{customer.email:<28}{customer.phone}"
            )
    except ValueError as exc:
        print_error(str(exc))


def handle_open_account(account_service: AccountService) -> None:
    print_header("Open Account")
    customer_id = prompt("Customer ID")
    branch_id = prompt("Branch ID")
    account_type = prompt("Account type (SAVINGS/CHECKING)", "SAVINGS")
    initial_deposit = prompt("Initial deposit (optional)", "0.00")
    try:
        account = account_service.open_account(
            int(customer_id),
            int(branch_id),
            account_type,
            Decimal(initial_deposit),
        )
        print_success(
            f"Account opened: {account.account_number} "
            f"(Type: {account.account_type}, Balance: ${account.balance:.2f})"
        )
    except ValueError as exc:
        print_error(str(exc))


def handle_deposit(account_service: AccountService) -> None:
    print_header("Deposit")
    account_number = prompt("Account number")
    amount = prompt("Amount")
    description = prompt("Description (optional)", "")
    try:
        transaction = account_service.deposit(
            account_number,
            Decimal(amount),
            description or None,
        )
        print_success(
            f"Deposit of ${transaction.amount:.2f} completed. "
            f"New balance: ${transaction.balance_after:.2f}"
        )
    except ValueError as exc:
        print_error(str(exc))


def handle_withdraw(account_service: AccountService) -> None:
    print_header("Withdraw")
    account_number = prompt("Account number")
    amount = prompt("Amount")
    description = prompt("Description (optional)", "")
    try:
        transaction = account_service.withdraw(
            account_number,
            Decimal(amount),
            description or None,
        )
        print_success(
            f"Withdrawal of ${transaction.amount:.2f} completed. "
            f"New balance: ${transaction.balance_after:.2f}"
        )
    except ValueError as exc:
        print_error(str(exc))


def handle_check_balance(account_service: AccountService) -> None:
    print_header("Check Balance")
    account_number = prompt("Account number")
    try:
        balance = account_service.check_balance(account_number)
        account = account_service.get_account(account_number)
        print_success(
            f"Account {account.account_number} ({account.account_type}) "
            f"balance: ${balance:.2f}"
        )
    except ValueError as exc:
        print_error(str(exc))


def main_menu() -> None:
    bank_service = BankService()
    branch_service = BranchService()
    customer_service = CustomerService()
    account_service = AccountService()

    while True:
        print_header("Banking System - Phase 1")
        print("  BANK")
        print("    1. Create Bank")
        print("    2. List Banks")
        print("  BRANCH")
        print("    3. Add Branch")
        print("    4. List Branches")
        print("  CUSTOMER")
        print("    5. Register Customer")
        print("    6. List Customers")
        print("  ACCOUNT")
        print("    7. Open Account")
        print("    8. Deposit")
        print("    9. Withdraw")
        print("   10. Check Balance")
        print("  OTHER")
        print("    0. Exit")
        print("-" * 50)

        choice = prompt("Select an option")

        if choice == "1":
            handle_create_bank(bank_service)
        elif choice == "2":
            handle_list_banks(bank_service)
        elif choice == "3":
            handle_add_branch(branch_service)
        elif choice == "4":
            handle_list_branches(branch_service)
        elif choice == "5":
            handle_register_customer(customer_service)
        elif choice == "6":
            handle_list_customers(customer_service)
        elif choice == "7":
            handle_open_account(account_service)
        elif choice == "8":
            handle_deposit(account_service)
        elif choice == "9":
            handle_withdraw(account_service)
        elif choice == "10":
            handle_check_balance(account_service)
        elif choice == "0":
            print("\nThank you for using the Banking System. Goodbye!")
            sys.exit(0)
        else:
            print_error("Invalid option. Please choose a number from the menu.")

        pause()


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
        sys.exit(0)
