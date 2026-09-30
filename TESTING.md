# SlideSolve Testing Strategy

Final suite: all 56 unittest tests passed. The recorded walkthrough shows the
earlier 46-test suite. Four 15-puzzle tests and six additional confidence tests
were added afterwards without changing the search algorithm.

## Additional confidence tests

`test_additional_confidence.py` constructs an independent BFS oracle for all
181,440 reachable 3x3 states. It checks solvability of reachable states and their
unsolvable twins, plus misplaced-tile and Manhattan admissibility and consistency
throughout the reachable state space. It compares Manhattan A* with one exact
representative at every depth 0–31 and all three heuristics at eight selected
depths. It also independently replays 100 seeded 4x4 generations. This does not
mean A* was executed on all 181,440 boards.

## Final 15-puzzle checks

The new suite builds exact distances through depth five from the 4x4 goal using
its own legal-swap implementation, independent of `board.neighbours`. All three
heuristics must return those distances and legal paths. It also checks a swapped
pair, the student's parity-invalid example, and a two-move 4x4 CLI demonstration.
This is shallow coverage, not exhaustive verification of all 15-puzzles.

The earlier 2x2 breadth-first search uses a separate search algorithm but shares
the production move generator. Its results alone cannot rule out shared bugs in
that generator. Move-property tests and the independent 4x4 generator provide
additional evidence.

## Why the tests use more than example answers

Tests written only for two or three familiar puzzles could pass even if the
search has a subtle general error. The Phase 3 suite therefore combines example
tests with properties and an independent shortest-path calculation.

## Test groups

### Validation

The suite checks empty input, non-square tile counts, duplicated and missing
tiles, non-integer text, booleans, invalid widths, and the accidental 1x1 case.

### Legal moves

Tests verify that corner and centre blanks have the correct number of moves,
that every move preserves the tile set, that exactly two positions change in a
move, and that every generated move can be reversed.

### Exhaustive 2x2 oracle

A breadth-first search starts at the 2x2 goal and visits all 12 reachable states.
Breadth-first search supplies the exact distance because every move has cost 1.
For every reachable state, the suite verifies that:

- zero, misplaced tiles, and Manhattan A* return the exact distance;
- the returned path consists only of legal moves;
- each heuristic is no greater than the exact remaining distance;
- each heuristic is consistent across every reachable edge.

All 24 permutations are also compared with the inversion-parity solvability
rule. Exactly the 12 states found by breadth-first search must be classified as
solvable.

### Seeded 3x3 scrambles

A fixed random seed creates reproducible legal scrambles of lengths 1 through
12. Uniform-cost search and Manhattan A* must agree on the optimal length, and
every returned transition must be legal. A solution may be shorter than the
scramble because a random scramble can partially undo earlier moves or take a
non-shortest route away from the goal.

### Boundary behaviour

Tests cover an already solved board, a zero expansion limit, invalid limits, an
unknown heuristic, an unsolvable board, and the known depth-31 8-puzzle.

## Defect discovered in Phase 3

The first Phase 3 run had 30 passing tests and one failure. The AI-generated
validation accepted `(0,)` as a 1x1 board when width was inferred, despite
rejecting an explicitly supplied width of 1. The minimum-width check had been
placed only in one branch. The implementation now checks the inferred width as
well, and the failing case remains as a regression test.
