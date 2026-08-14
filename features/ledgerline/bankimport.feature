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

  @LEDGER-BNK-003
  Scenario: A statement that arrives as a file
    When this file is read as a statement
      """
      date,amount,message
      2026-07-01,450.00,2026-0007
      2026-07-02,120.00,2026-0008
      """
    Then the file gives lines dated 2026-07-01 and 2026-07-02
    And the first line of the file is 45000 cents

  @LEDGER-BNK-004
  Scenario: Money leaving the account is a negative line
    When the statement for account NO-1 is imported
      | date       | cents | direction | reference | counterparty |
      | 2026-07-01 | 45000 | credit    | 2026-0007 | Bergstrom    |
      | 2026-07-02 | 12000 | debit     | refund    | Havn AS      |
    Then the ledger's amounts are 45000 and -12000

  @LEDGER-BNK-005
  Scenario: A bank line is matched to the invoice it pays
    Given the ledger is owed
      | number    | cents |
      | 2026-0007 | 45000 |
      | 2026-0008 | 12000 |
    When these lines are matched
      | date       | cents | reference           |
      | 2026-07-01 | 45000 | payment 2026-0007   |
      | 2026-07-02 | 12000 | 2026-0008 thank you |
    Then the lines are matched to 2026-0007 and 2026-0008

  Scenario: A line nobody can match is left for a person
    Given the ledger is owed
      | number    | cents |
      | 2026-0007 | 45000 |
    When these lines are matched
      | date       | cents | reference |
      | 2026-07-01 | 45000 | inv 7     |
    Then line 0 is left unmatched
    When a person matches line 0 to 2026-0007
    Then line 0 is matched to 2026-0007 by hand

  Scenario: A name in the bank's own character set survives the import
    When the bank's bytes are decoded as latin-1
    Then the name reads Sørensen
