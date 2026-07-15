Feature: A crew's day
  What a two-person crew is going to today, in the order they are going to it, with nobody
  promised the same two o'clock twice.

  Background:
    Given an empty board

  @FIELD-JOB-001
  Scenario: The day comes back in the order it is meant to happen
    Given these jobs are on the board
      | id  | crew  | day        | start | minutes | address      |
      | J-3 | north | 2026-07-16 | 14:00 | 60      | Storgata 4   |
      | J-1 | north | 2026-07-16 | 08:30 | 90      | Havnegata 12 |
      | J-2 | north | 2026-07-16 | 11:00 | 45      | Fjellveien 7 |
    When the north crew's day for 2026-07-16 is read
    Then the day is J-1, J-2 and J-3
