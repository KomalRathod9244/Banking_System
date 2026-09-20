# Banking System

A terminal-driven banking application built with **Python** and **PostgreSQL**, designed to practice object-oriented programming, relational database design, and layered application architecture.

The system models a real-world bank with multiple branches, customer accounts, fund transfers, transaction history, and a full loan lifecycle — all without a web framework or ORM.

---

## Features

### Phase 1 — Core Banking

| Feature | Description |
|---------|-------------|
| Bank management | Create and list banks |
| Branch management | Add and list branches under a bank |
| Customer management | Register customers at a branch |
| Account operations | Open savings/checking accounts |
| Deposits & withdrawals | Credit and debit with balance validation |
| Balance inquiry | Check account balance and status |

### Phase 2 — Transfers & Reporting

| Feature | Description |
|---------|-------------|
| Fund transfer | Atomic account-to-account transfers |
| Transaction history | View recent transactions per account |
| Branch reports | List branches by bank, customers by branch, accounts by branch |

### Phase 3 — Loan Management

| Feature | Description |
|---------|-------------|
| Loan application | Apply for Personal, Home, or Auto loans |
| Approval workflow | Approve or reject pending applications |
| Loan disbursement | Credit approved loan amount to customer account |
| Loan repayment | Deduct EMI/payments from linked account |
| EMI preview | Estimate monthly installment before applying |
| Payment history | Track all repayments against a loan |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| Database | PostgreSQL |
| DB Driver | `psycopg2-binary` |
| Configuration | `python-dotenv` |
| Interface | Terminal CLI (no web UI) |

**Intentionally excluded:** Flask, Django, SQLAlchemy, REST APIs, and frontend frameworks — keeping the focus on OOP and raw SQL.

---

## Architecture

The project follows a **layered architecture** with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│              CLI  (main.py)             │
│         User input & menu loop          │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│            Service Layer                │
│   Business rules, validation, workflow  │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│          Repository Layer               │
│      SQL queries, data persistence      │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│         PostgreSQL Database             │
└─────────────────────────────────────────┘
```

### Design Patterns Used

- **Repository Pattern** — isolates SQL from business logic
- **Service Layer** — enforces validation and orchestrates operations
- **Domain Models** — dataclasses representing database entities
- **Inheritance & Polymorphism** — loan product types (`PersonalLoan`, `HomeLoan`, `AutoLoan`)
- **Context Managers** — safe database connections with auto-commit/rollback

---

## Project Structure

```
Bank/
├── main.py                          # CLI entry point
├── requirements.txt
├── schema.sql                       # Full database schema
├── seed.sql                         # Demo bank and branches
├── .env.example                     # Environment variable template
├── migrations/
│   └── phase3.sql                   # Loan tables (existing DBs)
├── config/
│   └── settings.py                  # Loads DB config from .env
├── database/
│   └── connection.py                # Connection & cursor context managers
├── models/
│   ├── bank.py
│   ├── branch.py
│   ├── customer.py
│   ├── account.py
│   ├── transaction.py
│   ├── loan.py                      # Loan entity + product inheritance
│   └── loan_payment.py
├── repositories/
│   ├── bank_repository.py
│   ├── branch_repository.py
│   ├── customer_repository.py
│   ├── account_repository.py
│   ├── transaction_repository.py
│   ├── loan_repository.py
│   └── loan_payment_repository.py
├── services/
│   ├── bank_service.py
│   ├── branch_service.py
│   ├── customer_service.py
│   ├── account_service.py
│   └── loan_service.py
└── utils/
    └── validators.py                # Input validation helpers
```

---

## Prerequisites

- **Python** 3.10 or higher
- **PostgreSQL** 13+ installed and running
- **psql** CLI (bundled with PostgreSQL)

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd Bank
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv bvenv
bvenv\Scripts\activate

# macOS / Linux
python3 -m venv bvenv
source bvenv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
copy .env.example .env        # Windows
cp .env.example .env          # macOS / Linux
```

Edit `.env` with your PostgreSQL credentials:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=banking_system
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### 5. Create the database

```sql
CREATE DATABASE banking_system;
```

### 6. Run the schema

**Fresh database:**

```bash
psql -U postgres -d banking_system -f schema.sql
psql -U postgres -d banking_system -f seed.sql
```

**Existing database (adding loans after Phase 1 & 2):**

```bash
psql -U postgres -d banking_system -f migrations/phase3.sql
```

### 7. Run the application

```bash
python main.py
```

---

## CLI Menu Reference

| # | Section | Action |
|---|---------|--------|
| 1 | Bank | Create bank |
| 2 | Bank | List banks |
| 3 | Branch | Add branch |
| 4 | Branch | List branches |
| 5 | Customer | Register customer |
| 6 | Customer | List customers |
| 7 | Account | Open account |
| 8 | Account | Deposit |
| 9 | Account | Withdraw |
| 10 | Account | Check balance |
| 11 | Transfer | Transfer funds |
| 12 | History | Transaction history |
| 13 | Reports | List branches by bank |
| 14 | Reports | List customers by branch |
| 15 | Reports | List accounts by branch |
| 16 | Loans | Apply for loan |
| 17 | Loans | Approve loan |
| 18 | Loans | Reject loan |
| 19 | Loans | Disburse loan |
| 20 | Loans | Repay loan |
| 21 | Loans | View loan details |
| 22 | Loans | List customer loans |
| 23 | Loans | Loan payment history |
| 24 | Loans | Preview EMI |
| 0 | — | Exit |

---

## Database Schema

### Entity Relationships

```
Bank ──< Branch ──< Customer
              │         │
              │         └──< Account ──< Transaction
              │                │
              └──< Loan ────────┘ (disbursement account)
                    │
                    └──< LoanPayment
```

### Core Tables

| Table | Purpose |
|-------|---------|
| `banks` | Bank master data |
| `branches` | Branch locations linked to a bank |
| `customers` | Customer profiles linked to a branch |
| `accounts` | Savings/checking accounts with balance |
| `transactions` | Deposit, withdrawal, and transfer ledger |
| `loans` | Loan applications and active loans |
| `loan_payments` | Repayment history |

### Key Constraints

- Account balance cannot go below zero (`CHECK (balance >= 0)`)
- Customer email is unique across the system
- Account numbers are auto-generated (`ACC{branch_id}{6-digit random}`)
- Transfers and loan operations use `SELECT ... FOR UPDATE` for atomicity

---

## Loan Products (OOP)

Loan types are modeled using **inheritance** from a base `LoanProduct` class:

| Type | Default Rate | Max Tenure | Principal Range |
|------|-------------|------------|-----------------|
| **Personal** | 12.0% p.a. | 60 months | Rs. 10,000 – 5,00,000 |
| **Home** | 8.5% p.a. | 360 months | Rs. 1,00,000 – 50,00,000 |
| **Auto** | 10.0% p.a. | 84 months | Rs. 50,000 – 20,00,000 |

Each subclass implements:

- `calculate_emi()` — standard reducing-balance EMI formula
- `validate_application()` — principal and tenure limits
- `max_tenure_months()`, `min_principal()`, `max_principal()`

### Loan Lifecycle

```
APPLY ──► PENDING ──► APPROVED ──► DISBURSE ──► ACTIVE ──► REPAY ──► CLOSED
                └──► REJECTED
```

---

## Demo Workflow

After running `seed.sql`, a demo bank with two branches is available.

```
1. List Banks          →  Demo National Bank (ID: 1)
2. List Branches       →  Downtown & Uptown branches
3. Register Customer   →  Branch ID: 1
4. Open Account        →  Customer ID: 1, type: SAVINGS
5. Deposit             →  Fund the account
6. Apply for Loan      →  PERSONAL, Rs. 1,00,000, 24 months
7. Approve Loan        →  Loan ID: 1
8. Disburse Loan       →  Credit to customer account
9. Repay Loan          →  Partial or full repayment
10. View Loan Details   →  Check outstanding balance
```

---

## OOP Concepts Demonstrated

| Concept | Implementation |
|---------|----------------|
| **Classes & Objects** | `Bank`, `Customer`, `Account`, `Loan` dataclasses |
| **Encapsulation** | Private validation in services, properties on models |
| **Inheritance** | `LoanProduct` → `PersonalLoan`, `HomeLoan`, `AutoLoan` |
| **Polymorphism** | Each loan type overrides rate limits and EMI rules |
| **Composition** | `Branch` belongs to `Bank`; `Account` belongs to `Customer` |
| **Repository Pattern** | Data access separated from business logic |
| **Dependency Injection** | Services accept optional repository instances (testable) |

---

## Error Handling

- All user-facing errors return clear `[ERROR]` messages via the CLI
- Database operations use context managers — failed transactions are rolled back automatically
- Input validation covers email format, phone digits, positive amounts, and ID checks
- Insufficient balance and invalid state transitions (e.g. disbursing a non-approved loan) are blocked at the service layer

---

## License

This project is for educational purposes. Feel free to use and modify it for learning OOP and database programming.
