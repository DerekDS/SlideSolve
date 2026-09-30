# Heuristic Evaluation

## Method

The benchmark uses breadth-first search from the goal to establish exact puzzle
depths. This file contains depths 5, 10, 15, 20, 25, 30, with 162 runs across 18
distinct puzzles. The original submitted dataset used three puzzles per depth,
three trials per heuristic, and seed 20260927. A CSV alone does not record the
sampling seed; custom runs must record their own command separately.

Expanded states are the primary comparison because the count is deterministic
for this implementation. Runtime is reported as a median and should be treated
as supporting evidence because it is affected by the computer and background
activity.

## Results

| Exact depth | Heuristic | Mean expanded | Mean frontier | Median time (ms) | Reduction vs zero |
| ---: | --- | ---: | ---: | ---: | ---: |
| 5 | zero | 46.0 | 33.7 | 0.125 | 0.0% |
| 5 | misplaced | 7.0 | 9.0 | 0.044 | 84.8% |
| 5 | manhattan | 5.0 | 7.0 | 0.037 | 89.1% |
| 10 | zero | 597.3 | 361.0 | 1.509 | 0.0% |
| 10 | misplaced | 39.3 | 30.3 | 0.192 | 93.4% |
| 10 | manhattan | 19.3 | 16.3 | 0.135 | 96.8% |
| 15 | zero | 7,553.7 | 3,962.3 | 30.872 | 0.0% |
| 15 | misplaced | 372.3 | 238.0 | 1.944 | 95.1% |
| 15 | manhattan | 61.7 | 45.3 | 0.292 | 99.2% |
| 20 | zero | 47,115.3 | 17,277.7 | 231.897 | 0.0% |
| 20 | misplaced | 3,409.0 | 2,022.0 | 22.094 | 92.8% |
| 20 | manhattan | 606.7 | 361.7 | 4.532 | 98.7% |
| 25 | zero | 152,421.3 | 25,133.3 | 659.563 | 0.0% |
| 25 | misplaced | 28,515.0 | 12,847.3 | 166.251 | 81.3% |
| 25 | manhattan | 2,164.3 | 1,187.3 | 18.072 | 98.6% |
| 30 | zero | 181,376.7 | 24,671.3 | 736.285 | 0.0% |
| 30 | misplaced | 122,017.3 | 24,420.7 | 695.857 | 32.7% |
| 30 | manhattan | 21,285.0 | 9,374.3 | 148.933 | 88.3% |

## Main findings

- Every run returned the breadth-first-search solution length. Correctness
  mismatches: 0.
- At exact depth 30, uniform-cost search expanded an average of
  181,376.7 states. Misplaced tiles reduced this to
  122,017.3, a
  32.7% reduction.
- At the same depth, Manhattan distance expanded an average of
  21,285.0 states, a
  88.3% reduction from the zero
  heuristic.
- The differences are small for shallow puzzles and grow rapidly with depth.
  This agrees with A* theory: a more informative admissible heuristic avoids
  exploring states whose estimated total cost cannot improve the solution.

## Limitations

- The dataset contains 18 sampled 8-puzzles rather than every
  reachable state.
- Runtime measurements come from one machine and short searches are especially
  sensitive to timing noise.
- The implementation's deterministic tie-breaking affects exactly which states
  are expanded among states with equal priority.
- The comparison evaluates search effort, not heuristic calculation cost in
  isolation.
- Repeated deterministic runs are not additional independent puzzles. Median
  timing pools all runs per depth and heuristic. Execution order is fixed.
- The original machine and interpreter metadata were not fully recorded.
- These results do not measure 15-puzzle performance.
