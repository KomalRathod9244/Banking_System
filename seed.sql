-- Demo seed data for Phase 1 Banking System

INSERT INTO banks (name, code)
VALUES ('Demo National Bank', 'DNB001');

INSERT INTO branches (bank_id, name, address, phone)
VALUES
    (
        (SELECT id FROM banks WHERE code = 'DNB001'),
        'Downtown Branch',
        '100 Main Street, Downtown',
        '+1-555-0100'
    ),
    (
        (SELECT id FROM banks WHERE code = 'DNB001'),
        'Uptown Branch',
        '250 Park Avenue, Uptown',
        '+1-555-0200'
    );