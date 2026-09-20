-- Phase 1 Banking System Schema

CREATE TYPE account_type AS ENUM ('SAVINGS', 'CHECKING');
CREATE TYPE account_status AS ENUM ('ACTIVE', 'CLOSED', 'FROZEN');
CREATE TYPE transaction_type AS ENUM ('DEPOSIT', 'WITHDRAWAL');

CREATE TABLE banks (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    code VARCHAR(20) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE branches (
    id SERIAL PRIMARY KEY,
    bank_id INTEGER NOT NULL REFERENCES banks(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    phone VARCHAR(20),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (bank_id, name)
);

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    branch_id INTEGER NOT NULL REFERENCES branches(id) ON DELETE RESTRICT,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    branch_id INTEGER NOT NULL REFERENCES branches(id) ON DELETE RESTRICT,
    account_number VARCHAR(20) NOT NULL UNIQUE,
    account_type account_type NOT NULL DEFAULT 'SAVINGS',
    balance DECIMAL(15, 2) NOT NULL DEFAULT 0.00 CHECK (balance >= 0),
    status account_status NOT NULL DEFAULT 'ACTIVE',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    account_id INTEGER NOT NULL REFERENCES accounts(id) ON DELETE RESTRICT,
    transaction_type transaction_type NOT NULL,
    amount DECIMAL(15, 2) NOT NULL CHECK (amount > 0),
    balance_after DECIMAL(15, 2) NOT NULL,
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_branches_bank_id ON branches (bank_id);
CREATE INDEX idx_customers_branch_id ON customers (branch_id);
CREATE INDEX idx_customers_email ON customers (email);
CREATE INDEX idx_accounts_customer_id ON accounts (customer_id);
CREATE INDEX idx_accounts_branch_id ON accounts (branch_id);
CREATE INDEX idx_accounts_account_number ON accounts (account_number);
CREATE INDEX idx_transactions_account_id ON transactions (account_id);
CREATE INDEX idx_transactions_created_at ON transactions (created_at);

-- Phase 3: Loan Management

CREATE TYPE loan_type AS ENUM ('PERSONAL', 'HOME', 'AUTO');
CREATE TYPE loan_status AS ENUM ('PENDING', 'APPROVED', 'ACTIVE', 'CLOSED', 'REJECTED');

CREATE TABLE loans (
    id              SERIAL PRIMARY KEY,
    customer_id     INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    branch_id       INTEGER NOT NULL REFERENCES branches(id) ON DELETE RESTRICT,
    account_id      INTEGER REFERENCES accounts(id) ON DELETE RESTRICT,
    loan_type       loan_type NOT NULL,
    principal       DECIMAL(15, 2) NOT NULL CHECK (principal > 0),
    interest_rate   DECIMAL(5, 2) NOT NULL CHECK (interest_rate > 0),
    tenure_months   INTEGER NOT NULL CHECK (tenure_months > 0),
    emi             DECIMAL(15, 2) NOT NULL CHECK (emi > 0),
    outstanding     DECIMAL(15, 2) NOT NULL CHECK (outstanding >= 0),
    status          loan_status NOT NULL DEFAULT 'PENDING',
    created_at      TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    approved_at     TIMESTAMP,
    disbursed_at    TIMESTAMP
);

CREATE TABLE loan_payments (
    id                SERIAL PRIMARY KEY,
    loan_id           INTEGER NOT NULL REFERENCES loans(id) ON DELETE RESTRICT,
    amount            DECIMAL(15, 2) NOT NULL CHECK (amount > 0),
    outstanding_after DECIMAL(15, 2) NOT NULL CHECK (outstanding_after >= 0),
    created_at        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_loans_customer_id ON loans (customer_id);
CREATE INDEX idx_loans_branch_id ON loans (branch_id);
CREATE INDEX idx_loans_status ON loans (status);
CREATE INDEX idx_loan_payments_loan_id ON loan_payments (loan_id);