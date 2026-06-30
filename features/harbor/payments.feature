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

  @HARBOR-PAY-002
  Scenario: The rate on the day of the booking, not today's
    Given the marina charges 5200 cents a night from 2026-08-01
    And Kittiwake has berth A1 from 2026-07-01 to 2026-07-05 as H-1001
    When the invoice for H-1001 is made out as 2026-0002
    Then the invoice totals 18000 cents

  @HARBOR-PAY-003
  Scenario: The card is charged when the booking is confirmed
    When H-1001 is confirmed for 18000 cents
    Then the card has been charged 18000 cents for H-1001

  Scenario: The guest comes back from the bank's page to their own booking
    Given H-1001 sends the guest away to pay with token tok-9
    And H-1002 sends the guest away to pay with token tok-4
    When the guest comes back with token tok-9
    Then they are put back on booking H-1001
