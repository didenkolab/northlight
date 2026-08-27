Feature: Tax rates, quarters, and closing one
  A quarter that has gone to the tax office has to stay what it was when it went, and the
  rate on an invoice is the rate that applied the day it was written.

  Background:
    Given an empty ledger

  @LEDGER-TAX-001
  Scenario: The tax is rounded on every line
    When the tax on these lines is worked out per-line
      | net_cents | tax_percent |
      | 333       | 25          |
      | 333       | 25          |
      | 333       | 25          |
    Then the tax comes to 249 cents

  @LEDGER-TAX-002
  Scenario: The tax is rounded once, on the total
    When the tax on these lines is worked out per-invoice
      | net_cents | tax_percent |
      | 333       | 25          |
      | 333       | 25          |
      | 333       | 25          |
    Then the tax comes to 250 cents

  @LEDGER-TAX-003
  Scenario: A closed quarter takes nothing more
    Given the quarter 2026-Q3 is closed
    When an entry dated 2026-08-15 is booked
    Then the entry is refused because 2026-Q3 is closed

  @LEDGER-TAX-004
  Scenario: The rate that applied on the day of the invoice
    Given the tax rate was 25 from 2020-01-01 and 22 from 2026-09-01
    When the rate for 2026-08-31 is looked up
    Then the rate is 25

  Scenario: The last day of March is in the first quarter
    When the quarter of 2026-03-31 is worked out
    Then the quarter is 2026-Q1
