Feature: Invoice numbers and the lines under them
  A tax office reads the sequence of invoice numbers, and a gap in it is a question
  somebody has to answer. Under the number, the lines, and the tax against each of them.

  Background:
    Given the ledger has issued no invoices

  @LEDGER-INV-001
  Scenario: Invoice numbers run without a gap in them
    When 3 invoices are numbered for 2026
    Then the numbers are 2026-0001, 2026-0002 and 2026-0003
