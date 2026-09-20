-- Phase 3: Loan Management
-- Run on existing database: psql -U postgres -d banking_system -f migrations/phase3.sql

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
