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

  @HARBOR-BKG-003
  Scenario: The morning a boat leaves, its berth is somebody else's night
    Given Kittiwake has berth A1 from 2026-07-01 to 2026-07-05 as H-1001
    When Puffin books berth A1 from 2026-07-05 to 2026-07-09 as H-1002
    Then the booking is taken

  Scenario: The marina's own spreadsheet becomes a berth list
    When the marina's berth spreadsheet is imported
    Then the berths read are A1, A2 and B7
    And berth A1 has shore power
    And berth A2 has no shore power

  @HARBOR-BKG-006
  Scenario: A berth is held for twenty minutes while the guest pays
    When Puffin holds berth A2 from 2026-07-01 to 2026-07-03 as H-1003 at 10:00
    Then the hold is taken
    And the hold runs out at 10:20

  Scenario: A cancelled booking gives its nights back to the free list
    Given Kittiwake has berth A1 from 2026-07-01 to 2026-07-05 as H-1001
    When booking H-1001 is cancelled
    Then the free berths from 2026-07-02 to 2026-07-04 are A1, A2 and B7
    And the cancellation says it gave back berth A1

  Scenario: Two guests clicking at the same moment do not both get the berth
    Given Puffin holds berth A2 from 2026-07-01 to 2026-07-03 as H-1003 at 10:00
    When Guillemot holds berth A2 from 2026-07-02 to 2026-07-04 as H-1004 at 10:01
    Then the hold is refused because berth held

  @HARBOR-BKG-005
  Scenario: The free berths come back in the marina's own order
    Given the marina has berths B7, A2 and A1
    When the office asks which berths are free from 2026-07-02 to 2026-07-04
    Then the free berths are A1, A2 and B7
