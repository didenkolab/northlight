Feature: What a stay costs and who pays for it
  An invoice for the nights the boat was here, at the price the marina was charging on the
  day the booking was made, and a card charged once for it however many times the guest
  presses the button.

  Background:
    Given the marina has berths A1, A2 and B7
    And the marina charges 4500 cents a night from 2026-01-01

  @HARBOR-PAY-001
  Scenario: An invoice for the nights that were booked
    Given Kittiwake has berth A1 from 2026-07-01 to 2026-07-05 as H-1001
    When the invoice for H-1001 is made out as 2026-0001
    Then the invoice totals 18000 cents
    And the invoice is numbered 2026-0001
