Feature: Berth booking
  A berth belongs to one boat for a range of nights. Before the marina can sell a week it
  has to know which berths are free for it, and it has to keep saying no to the second
  guest who wants the same one.

  Background:
    Given the marina has berths A1, A2 and B7

  @HARBOR-BKG-001
  Scenario: A boat takes a berth for a range of nights
    When Kittiwake books berth A1 from 2026-07-01 to 2026-07-05 as H-1001
    Then the booking is taken
    And the calendar holds H-1001

  @HARBOR-BKG-002
  Scenario: A second boat cannot have nights that are already sold
    Given Kittiwake has berth A1 from 2026-07-01 to 2026-07-05 as H-1001
    When Puffin books berth A1 from 2026-07-03 to 2026-07-08 as H-1002
    Then the booking is refused because berth taken
    And the refusal names H-1001

  @HARBOR-BKG-004
  Scenario: The berths that are free for a week
    Given Kittiwake has berth A1 from 2026-07-01 to 2026-07-05 as H-1001
    When the office asks which berths are free from 2026-07-02 to 2026-07-04
    Then the free berths are A2 and B7
