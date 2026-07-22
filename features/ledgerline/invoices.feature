Feature: Invoice numbers and the lines under them
  A tax office reads the sequence of invoice numbers, and a gap in it is a question
  somebody has to answer. Under the number, the lines, and the tax against each of them.

  Background:
    Given the ledger has issued no invoices

  @LEDGER-INV-001
  Scenario: Invoice numbers run without a gap in them
    When 3 invoices are numbered for 2026
    Then the numbers are 2026-0001, 2026-0002 and 2026-0003

  @LEDGER-INV-002
  Scenario: A new business year starts the sequence again
    Given 2 invoices are numbered for 2026
    When 1 invoice is numbered for 2027
    Then the numbers are 2026-0001, 2026-0002 and 2027-0001

  @LEDGER-INV-003
  Scenario: Every line shows the tax it is charged
    When an invoice is composed for Bergstrom Accounting
      | description | quantity | unit_cents | tax_percent |
      | Bookkeeping | 10       | 8000       | 25          |
      | Year end    | 1        | 45000      | 25          |
    Then line 1 shows 80000 net, 20000 tax and 100000 gross

  @LEDGER-INV-004
  Scenario: The totals underneath add the lines up
    When an invoice is composed for Bergstrom Accounting
      | description | quantity | unit_cents | tax_percent |
      | Bookkeeping | 10       | 8000       | 25          |
      | Year end    | 1        | 45000      | 25          |
    Then the invoice totals 125000 net, 31250 tax and 156250 gross

  Scenario: Two invoices numbered from the same reading do not get the same number
    Given 1 invoice is numbered for 2026
    When two invoices are numbered from one reading of the sequence for 2026
    Then the second one is refused because the sequence has moved on

  @LEDGER-INV-005
  Scenario: A refund is a credit note against the invoice it undoes
    Given an invoice 2026-0007 for Bergstrom Accounting
      | description | quantity | unit_cents | tax_percent |
      | Bookkeeping | 10       | 8000       | 25          |
    When 20000 cents are credited against it as 2026-C002
    Then the credit note is made out against 2026-0007
    And crediting 200000 cents is refused because more than the invoice it credits

  Scenario: A late invoice is chased twice and then left alone
    Given an invoice fell due on 2026-07-01
    When it is 2026-07-09 and nothing has been chased yet
    Then a reminder goes out
    When it is 2026-08-05 and 1 reminder has been sent
    Then a reminder goes out
    When it is 2026-09-01 and 2 reminders have been sent
    Then no reminder goes out because chased twice already
