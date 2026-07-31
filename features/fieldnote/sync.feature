Feature: Putting a phone back together with the board
  A crew phone that has been dark since breakfast, and a dispatcher's board that has
  carried on without it. Between them they know what the day was.

  Background:
    Given nothing on the phone and nothing on the board

  @FIELD-SYN-001
  Scenario: Work done with the phone offline survives the sync
    Given the board has these jobs
      | id  | crew  | status  |
      | J-1 | north | planned |
    And the phone has these jobs
      | id  | crew  | status |
      | J-1 | north | done   |
    When the phone and the board are merged
    Then J-1 comes back as done

  @FIELD-SYN-002
  Scenario: A job the phone has never seen comes down from the board
    Given the board has these jobs
      | id  | crew  | status  |
      | J-1 | north | planned |
      | J-2 | north | planned |
    And the phone has these jobs
      | id  | crew  | status |
      | J-1 | north | done   |
    When the phone and the board are merged
    Then the merged day is J-1 and J-2

  Scenario: The edits made while the phone was dark are replayed in the order they were made
    Given the board has these jobs
      | id  | crew  | status  |
      | J-1 | north | planned |
    And the phone queued these edits
      | id  | field  | value      |
      | J-1 | status | on the way |
      | J-1 | status | done       |
    When the queued edits are replayed onto the board
    Then J-1 comes back as done

  @FIELD-SYN-003
  Scenario: What the two sides disagreed about is written down
    Given the board has these jobs
      | id  | crew  | status  |
      | J-1 | north | planned |
    And the phone has these jobs
      | id  | crew  | status |
      | J-1 | north | done   |
    When the phone and the board are merged
    Then the merge reports J-1 as done on the phone and planned on the board
