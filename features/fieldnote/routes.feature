Feature: Ordering a crew's day
  Eleven stops and one van. Not the shortest day that could exist, but one that never
  sends the van back past a house it has already been to.

  Background:
    Given the roads we know
      | from  | to    | minutes |
      | depot | north | 20      |
      | depot | west  | 35      |
      | depot | east  | 50      |
      | north | west  | 25      |
      | north | east  | 40      |
      | west  | east  | 30      |

  @FIELD-RTE-001
  Scenario: The nearest stop first
    When the stops north, west and east are ordered from depot
    Then the order is north, west and east

  @FIELD-RTE-002
  Scenario: A road we have never driven is guessed from the distance
    Given where the stops are
      | stop  | x  | y  |
      | depot | 0  | 0  |
      | north | 0  | 20 |
      | west  | 30 | 0  |
      | east  | 40 | 40 |
      | isle  | 0  | 60 |
    When the leg from north to isle is worked out
    Then the leg is 52 minutes

  @FIELD-RTE-003
  Scenario: The depot is both ends of the day
    Given where the stops are
      | stop  | x  | y  |
      | depot | 0  | 0  |
      | north | 0  | 20 |
      | west  | 30 | 0  |
      | east  | 40 | 40 |
    When the day through north, west and east is planned from depot
    Then the plan is depot, north, west, east and depot
