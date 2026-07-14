Feature: Importing a bank statement
  Three banks and three ideas of what a statement is. What the ledger keeps is a date, an
  amount in cents, and whatever the payer typed in the reference.

  Background:
    Given an empty ledger

  @LEDGER-BNK-001
  Scenario: A statement is imported into the ledger
    When the statement for account NO-1 is imported
      | date       | cents | reference | counterparty |
      | 2026-07-01 | 45000 | 2026-0007 | Bergstrom    |
      | 2026-07-02 | 12000 | 2026-0008 | Havn AS      |
    Then the ledger holds lines dated 2026-07-01 and 2026-07-02

  @LEDGER-BNK-002
  Scenario: The same statement twice is the same statement
    Given the statement for account NO-1 is imported
      | date       | cents | reference | counterparty |
      | 2026-07-01 | 45000 | 2026-0007 | Bergstrom    |
    When the statement for account NO-1 is imported
      | date       | cents | reference | counterparty |
      | 2026-07-01 | 45000 | 2026-0007 | Bergstrom    |
    Then the import is recognised as one we already have
    And the ledger holds lines dated 2026-07-01
