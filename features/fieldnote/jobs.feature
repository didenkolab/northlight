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

  @FIELD-JOB-002
  Scenario: A crew cannot be in two places at two o'clock
    Given these jobs are on the board
      | id  | crew  | day        | start | minutes | address    |
      | J-1 | north | 2026-07-16 | 14:00 | 60      | Storgata 4 |
    When J-2 is put on the north crew for 2026-07-16 at 14:30 for 30 minutes
    Then the job is refused because the crew is already out
    And the job in the way is J-1

  @FIELD-JOB-003
  Scenario: A job is handed to another crew from the board
    Given these jobs are on the board
      | id  | crew  | day        | start | minutes | address    |
      | J-1 | north | 2026-07-16 | 14:00 | 60      | Storgata 4 |
    When J-1 is handed to the south crew
    Then the job is taken
    And the south crew's day for 2026-07-16 is J-1
