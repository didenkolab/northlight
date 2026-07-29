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
