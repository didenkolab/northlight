Feature: Checking a guest in from the pontoon
  The pontoon is where the guests are and where the signal is not, so a check-in is made
  on the phone and goes up when there is something to send it to.

  Background:
    Given the marina has berths A1, A2 and B7

  @HARBOR-CHK-001
  Scenario: A guest is checked in with no signal to check them in on
    Given the phone has no signal
    When ola checks H-1001 in at 09:40
    Then the phone is holding H-1001
    When the phone finds a signal
    Then the office has H-1001 as arrived

  @HARBOR-CHK-002
  Scenario: A morning's queue goes up in the order it happened
    Given the phone has no signal
    When ola checks H-1003 in at 16:30
    And ola checks H-1001 in at 09:40
    And ola checks H-1002 in at 11:15
    And the phone finds a signal
    Then the office has H-1001, H-1002 and H-1003 as arrived

  @HARBOR-CHK-003
  Scenario: The code painted on the berth opens the right booking
    Given Kittiwake has berth A1 from 2026-07-01 to 2026-07-05 as H-1001
    And berth A1 is painted with code NL-A1
    When the crew scan NL-A1 on 2026-07-02
    Then the scan opens booking H-1001

  @HARBOR-CHK-004
  Scenario: A phone with the wrong clock keeps the order it saw
    Given the phone has no signal
    When ola checks H-1001 in at 09:40
    And ola checks H-1002 in at 10:10
    And the phone's clock is put right by 95 minutes
    And the phone finds a signal
    Then the check-ins are stamped 11:15 and 11:45
