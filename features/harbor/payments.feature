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

  @HARBOR-PAY-005
  Scenario: A retried confirmation charges the card once
    Given H-1001 is confirmed for 18000 cents with intent conf-1
    And H-1043 is confirmed for 9000 cents with intent conf-2
    When H-1001 is confirmed for 18000 cents with intent conf-1
    Then the card has been charged 18000 cents for H-1001
    And the ledger holds 2 charges

  @HARBOR-PAY-006
  Scenario: A deposit now and the rest on arrival
    When 18000 cents is split into a 30 per cent deposit
    Then 5400 cents is taken now and 12600 cents on arrival

  Scenario: A stay of a month or more is priced by the month
    Given the marina charges 90000 cents a month from 2026-01-01
    And Kittiwake has berth A1 from 2026-06-01 to 2026-07-01 as H-2001
    When the invoice for H-2001 is made out as 2026-0044
    Then the invoice totals 90000 cents

  @HARBOR-PAY-004
  Scenario: A refund larger than the invoice it credits is refused
    Given H-1001 is confirmed for 18000 cents with intent conf-1
    When 25000 cents are refunded to H-1001
    Then the refund is refused because more than was charged
