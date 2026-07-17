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
