#!/usr/bin/env python3

"""Banking System - Terminal CLI (Phase 1 + Phase 2 + Phase 3)."""

import sys
from decimal import Decimal

from services.account_service import AccountService
from services.bank_service import BankService
from services.branch_service import BranchService
from services.customer_service import CustomerService
from services.loan_service import LoanService


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
            f"(Type: {account.account_type}, Balance: Rs.{account.balance:.2f})"
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
            f"Deposit of Rs.{transaction.amount:.2f} completed. "
            f"New balance: Rs.{transaction.balance_after:.2f}"
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
            f"Withdrawal of Rs.{transaction.amount:.2f} completed. "
            f"New balance: Rs.{transaction.balance_after:.2f}"
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
            f"balance: Rs.{balance:.2f}"
        )
    except ValueError as exc:
        print_error(str(exc))


def handle_transfer(account_service: AccountService) -> None:
    print_header("Transfer Funds")
    from_account = prompt("From account number")
    to_account = prompt("To account number")
    amount = prompt("Amount")
    description = prompt("Description (optional)", "")
    try:
        withdrawal_tx, deposit_tx = account_service.transfer(
            from_account,
            to_account,
            Decimal(amount),
            description or None,
        )
        print_success(
            f"Transfer of Rs.{withdrawal_tx.amount:.2f} completed.\n"
            f"  From {from_account}: new balance Rs.{withdrawal_tx.balance_after:.2f}\n"
            f"  To   {to_account}: new balance Rs.{deposit_tx.balance_after:.2f}"
        )
    except ValueError as exc:
        print_error(str(exc))


def handle_transaction_history(account_service: AccountService) -> None:
    print_header("Transaction History")
    account_number = prompt("Account number")
    limit = prompt("Number of records (default 20)", "20")
    try:
        transactions = account_service.get_transaction_history(
            account_number, int(limit)
        )
        if not transactions:
            print("No transactions found for this account.")
            return
        print(f"\nTransactions for {account_number}:")
        print(
            f"{'ID':<6}{'Type':<12}{'Amount':<14}{'Balance':<14}"
            f"{'Date':<22}{'Description'}"
        )
        print("-" * 90)
        for tx in transactions:
            desc = (tx.description or "-")[:30]
            print(
                f"{tx.id:<6}{tx.transaction_type:<12}Rs.{tx.amount:<12.2f}"
                f"Rs.{tx.balance_after:<12.2f}{str(tx.created_at):<22}{desc}"
            )
    except ValueError as exc:
        print_error(str(exc))


def handle_list_branches_by_bank(branch_service: BranchService) -> None:
    print_header("List Branches by Bank")
    bank_id = prompt("Bank ID")
    try:
        branches = branch_service.list_branches_by_bank(int(bank_id))
        if not branches:
            print("No branches found for this bank.")
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


def handle_list_customers_by_branch(customer_service: CustomerService) -> None:
    print_header("List Customers by Branch")
    branch_id = prompt("Branch ID")
    try:
        customers = customer_service.list_customers_by_branch(int(branch_id))
        if not customers:
            print("No customers found for this branch.")
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


def handle_list_accounts_by_branch(account_service: AccountService) -> None:
    print_header("List Accounts by Branch")
    branch_id = prompt("Branch ID")
    try:
        accounts = account_service.list_accounts_by_branch(int(branch_id))
        if not accounts:
            print("No accounts found for this branch.")
            return
        print(
            f"{'ID':<6}{'Account No':<16}{'Customer':<10}"
            f"{'Type':<10}{'Balance':<14}{'Status'}"
        )
        print("-" * 70)
        for account in accounts:
            print(
                f"{account.id:<6}{account.account_number:<16}{account.customer_id:<10}"
                f"{account.account_type:<10}Rs.{account.balance:<12.2f}{account.status}"
            )
    except ValueError as exc:
        print_error(str(exc))


def handle_apply_loan(loan_service: LoanService) -> None:
    print_header("Apply for Loan")
    customer_id = prompt("Customer ID")
    branch_id = prompt("Branch ID")
    loan_type = prompt("Loan type (PERSONAL/HOME/AUTO)", "PERSONAL")
    principal = prompt("Principal amount")
    tenure = prompt("Tenure in months")
    try:
        loan = loan_service.apply_for_loan(
            int(customer_id),
            int(branch_id),
            loan_type,
            Decimal(principal),
            int(tenure),
        )
        print_success(
            f"Loan application submitted (ID: {loan.id}).\n"
            f"  Type: {loan.loan_type}  |  Principal: Rs.{loan.principal:.2f}\n"
            f"  Rate: {loan.interest_rate}%  |  Tenure: {loan.tenure_months} months\n"
            f"  EMI: Rs.{loan.emi:.2f}  |  Status: {loan.status}"
        )
    except ValueError as exc:
        print_error(str(exc))


def handle_approve_loan(loan_service: LoanService) -> None:
    print_header("Approve Loan")
    loan_id = prompt("Loan ID")
    try:
        loan = loan_service.approve_loan(int(loan_id))
        print_success(f"Loan {loan.id} approved. Status: {loan.status}")
    except ValueError as exc:
        print_error(str(exc))


def handle_reject_loan(loan_service: LoanService) -> None:
    print_header("Reject Loan")
    loan_id = prompt("Loan ID")
    try:
        loan = loan_service.reject_loan(int(loan_id))
        print_success(f"Loan {loan.id} rejected. Status: {loan.status}")
    except ValueError as exc:
        print_error(str(exc))


def handle_disburse_loan(loan_service: LoanService) -> None:
    print_header("Disburse Loan")
    loan_id = prompt("Loan ID")
    account_number = prompt("Customer account number (for disbursement)")
    try:
        loan = loan_service.disburse_loan(int(loan_id), account_number)
        print_success(
            f"Loan {loan.id} disbursed.\n"
            f"  Amount: Rs.{loan.principal:.2f} credited to account.\n"
            f"  Outstanding: Rs.{loan.outstanding:.2f}  |  Status: {loan.status}"
        )
    except ValueError as exc:
        print_error(str(exc))


def handle_repay_loan(loan_service: LoanService) -> None:
    print_header("Repay Loan")
    loan_id = prompt("Loan ID")
    amount = prompt("Repayment amount")
    try:
        loan, payment = loan_service.repay_loan(int(loan_id), Decimal(amount))
        status_msg = "Loan fully repaid and CLOSED." if loan.status == "CLOSED" else ""
        print_success(
            f"Repayment of Rs.{payment.amount:.2f} recorded.\n"
            f"  Outstanding: Rs.{loan.outstanding:.2f}  |  Status: {loan.status}\n"
            f"  {status_msg}"
        )
    except ValueError as exc:
        print_error(str(exc))


def handle_view_loan(loan_service: LoanService) -> None:
    print_header("View Loan Details")
    loan_id = prompt("Loan ID")
    try:
        loan = loan_service.get_loan(int(loan_id))
        print(f"\nLoan #{loan.id}")
        print(f"  Customer ID  : {loan.customer_id}")
        print(f"  Branch ID    : {loan.branch_id}")
        print(f"  Type         : {loan.loan_type}")
        print(f"  Principal    : Rs.{loan.principal:.2f}")
        print(f"  Interest Rate: {loan.interest_rate}% p.a.")
        print(f"  Tenure       : {loan.tenure_months} months")
        print(f"  EMI          : Rs.{loan.emi:.2f}")
        print(f"  Outstanding  : Rs.{loan.outstanding:.2f}")
        print(f"  Status       : {loan.status}")
        print(f"  Account ID   : {loan.account_id or 'Not linked'}")
        print(f"  Applied On   : {loan.created_at}")
        if loan.approved_at:
            print(f"  Approved On  : {loan.approved_at}")
        if loan.disbursed_at:
            print(f"  Disbursed On : {loan.disbursed_at}")
    except ValueError as exc:
        print_error(str(exc))


def handle_list_customer_loans(loan_service: LoanService) -> None:
    print_header("List Customer Loans")
    customer_id = prompt("Customer ID")
    try:
        loans = loan_service.list_loans_by_customer(int(customer_id))
        if not loans:
            print("No loans found for this customer.")
            return
        print(
            f"{'ID':<6}{'Type':<10}{'Principal':<14}{'EMI':<12}"
            f"{'Outstanding':<14}{'Status':<10}{'Tenure'}"
        )
        print("-" * 80)
        for loan in loans:
            print(
                f"{loan.id:<6}{loan.loan_type:<10}Rs.{loan.principal:<12.2f}"
                f"Rs.{loan.emi:<10.2f}Rs.{loan.outstanding:<12.2f}"
                f"{loan.status:<10}{loan.tenure_months} mo"
            )
    except ValueError as exc:
        print_error(str(exc))


def handle_loan_payment_history(loan_service: LoanService) -> None:
    print_header("Loan Payment History")
    loan_id = prompt("Loan ID")
    limit = prompt("Number of records (default 20)", "20")
    try:
        payments = loan_service.get_payment_history(int(loan_id), int(limit))
        if not payments:
            print("No payments found for this loan.")
            return
        print(f"\nPayments for Loan #{loan_id}:")
        print(f"{'ID':<6}{'Amount':<14}{'Outstanding':<14}{'Date'}")
        print("-" * 50)
        for payment in payments:
            print(
                f"{payment.id:<6}Rs.{payment.amount:<12.2f}"
                f"Rs.{payment.outstanding_after:<12.2f}{payment.created_at}"
            )
    except ValueError as exc:
        print_error(str(exc))


def handle_preview_emi(loan_service: LoanService) -> None:
    print_header("Preview EMI")
    loan_type = prompt("Loan type (PERSONAL/HOME/AUTO)", "PERSONAL")
    principal = prompt("Principal amount")
    tenure = prompt("Tenure in months")
    try:
        emi = loan_service.preview_emi(loan_type, Decimal(principal), int(tenure))
        print_success(f"Estimated EMI: Rs.{emi:.2f} per month")
    except ValueError as exc:
        print_error(str(exc))


def main_menu() -> None:
    bank_service = BankService()
    branch_service = BranchService()
    customer_service = CustomerService()
    account_service = AccountService()
    loan_service = LoanService()

    while True:
        print_header("Banking System - Phase 3")
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
        print("  TRANSFER & HISTORY")
        print("   11. Transfer Funds")
        print("   12. Transaction History")
        print("  BRANCH REPORTS")
        print("   13. List Branches by Bank")
        print("   14. List Customers by Branch")
        print("   15. List Accounts by Branch")
        print("  LOANS")
        print("   16. Apply for Loan")
        print("   17. Approve Loan")
        print("   18. Reject Loan")
        print("   19. Disburse Loan")
        print("   20. Repay Loan")
        print("   21. View Loan Details")
        print("   22. List Customer Loans")
        print("   23. Loan Payment History")
        print("   24. Preview EMI")
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
        elif choice == "11":
            handle_transfer(account_service)
        elif choice == "12":
            handle_transaction_history(account_service)
        elif choice == "13":
            handle_list_branches_by_bank(branch_service)
        elif choice == "14":
            handle_list_customers_by_branch(customer_service)
        elif choice == "15":
            handle_list_accounts_by_branch(account_service)
        elif choice == "16":
            handle_apply_loan(loan_service)
        elif choice == "17":
            handle_approve_loan(loan_service)
        elif choice == "18":
            handle_reject_loan(loan_service)
        elif choice == "19":
            handle_disburse_loan(loan_service)
        elif choice == "20":
            handle_repay_loan(loan_service)
        elif choice == "21":
            handle_view_loan(loan_service)
        elif choice == "22":
            handle_list_customer_loans(loan_service)
        elif choice == "23":
            handle_loan_payment_history(loan_service)
        elif choice == "24":
            handle_preview_emi(loan_service)
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
