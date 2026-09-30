# SlideSolve

SlideSolve is a command-line A* solver for sliding-tile puzzles, built for
Programming Assignment 1, Track B. It validates puzzle input, detects impossible
boards, finds an optimal solution, displays the move sequence, and reports
search statistics. It can also generate reproducible solvable puzzles.

The supported heuristics are:

- `zero`, which turns A* into uniform-cost search;
- `misplaced`, which counts numbered tiles outside their goal positions;
- `manhattan`, the default, which sums numbered tiles' grid distances from
  their goal positions.

The blank is represented by `0` in input and `_` when a board is displayed.

## Requirements

- Python 3.11 or newer
- No runtime packages outside the Python standard library

## Run from the project folder

The source lives under `src`, so set `PYTHONPATH` before running it directly:

```powershell
$env:PYTHONPATH = "src"
python -m slidesolve --help
```

If `python` is not available, select or install a Python 3.11+ interpreter in
VS Code using **Python: Select Interpreter**.

## Solve a puzzle

```powershell
python -m slidesolve solve "1,2,3,4,0,6,7,5,8"
```

Show every board in the solution:

```powershell
python -m slidesolve solve "1,2,3,4,0,6,7,5,8" --show-boards
```

Choose a heuristic:

```powershell
python -m slidesolve solve "1,3,6,5,0,2,4,7,8" --heuristic misplaced
```

Limit the work for a difficult puzzle:

```powershell
python -m slidesolve solve "8,6,7,2,5,4,3,0,1" --max-expanded 50000
```

Use compact output:

```powershell
python -m slidesolve solve "1,2,3,4,5,6,7,0,8" --quiet
```

## Generate a puzzle

```powershell
python -m slidesolve generate --moves 25 --seed 42
```

Generation begins at the goal and makes legal moves, so its output is always
solvable. The seed makes a generated puzzle reproducible. The number of scramble
moves is not necessarily the optimal solution length because a scramble can
revisit a state through a longer route.

## Run in VS Code

1. Install the Microsoft Python extension if it is not already installed.
2. Run **Python: Select Interpreter** and choose Python 3.11 or newer.
3. Open **Run and Debug**.
4. Choose either **SlideSolve: solve example** or
   **SlideSolve: generate puzzle**.
5. Press the green run button or `F5`.

The included `.vscode/launch.json` runs Python in the integrated terminal. It
does not open a browser or require a localhost server.

## Run the tests

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests -v
```

The suite contains 56 tests covering validation, legal moves, exhaustive 2x2
correctness, heuristic admissibility and consistency, seeded random scrambles,
the depth-31 8-puzzle, generation, CLI output, error handling, and benchmark
reproducibility. Four later tests add 4x4 parity, CLI, and shallow exact-depth
checks using an independent move generator. Six further tests in
`test_additional_confidence.py` build an independent BFS oracle for all 181,440
reachable 3x3 states, check solvability and heuristic properties exhaustively,
compare A* on representative boards across depths 0–31, and replay 100 seeded
4x4 generations. The video correctly describes the 46 tests present at recording.

## 15-puzzle support

The solver also accepts 4x4 boards containing 0 through 15. For example:

```powershell
python -m slidesolve solve "1,2,3,4,5,6,7,8,9,10,11,12,13,0,14,15" --show-boards --max-expanded 100000
python -m slidesolve generate --width 4 --moves 10 --seed 42
```

The first example takes two moves: `right right`. Difficult 15-puzzles can use
substantial time and memory. An expansion limit bounds expanded states, not
memory or wall-clock time. Performance results below concern the 8-puzzle only;
the project does not claim practical performance on arbitrary 15-puzzles.

## Reproduce the heuristic evaluation

The benchmark uses breadth-first search to sample puzzles at known exact depths
of 5, 10, 15, 20, 25, and 30 moves. It runs every heuristic three times on
three puzzles at each depth.

```powershell
$env:PYTHONPATH = "src"
python -m slidesolve.benchmark --output results/heuristic_comparison.csv --samples 3 --repeats 3 --seed 20260927
python scripts/analyze_benchmark.py
```

The commands regenerate the CSV files and analysis:

- `results/heuristic_comparison.csv`: all 162 raw runs;
- `results/heuristic_summary.csv`: aggregates by depth and heuristic;
- `results/ANALYSIS.md`: method, results, findings, and limitations;

`results/heuristic_evaluation.xlsx` is an additional static presentation of the
original results, created separately with Codex's spreadsheet tools. The commands
above do not regenerate that workbook.

At exact depth 30, Manhattan distance reduced average expanded states from
181,376.7 with the zero heuristic to 21,285.0, an 88.3% reduction. Expanded
states are the primary metric; runtime is supporting evidence because it is
machine-dependent.

See [TESTING.md](TESTING.md) for the testing strategy,
[AI_NOTES.md](AI_NOTES.md) for the AI-use development log.

## Report and walkthrough

- [Written report](report/AdvAlg%20Ass1%20Report.pdf)
- [Recorded walkthrough](video/SlideSolve_Walkthrough.mp4) (included in the clean submission package)

The video was recorded before the ten additional tests were added. Its
reference to 46 tests describes that version; the final suite contains 56.

## Project layout

```text
src/slidesolve/
├── astar.py        A* search and path reconstruction
├── board.py        validation, parsing, moves, and formatting
├── cli.py          command-line interface
├── benchmark.py    reproducible exact-depth heuristic evaluation
├── generator.py    reproducible solvable puzzle generation
├── heuristics.py   zero, misplaced, and Manhattan heuristics
└── solvability.py  inversion counting and parity checks

tests/
├── test_phase2_core.py
├── test_phase3_edge_cases.py
├── test_phase4_cli.py
├── test_phase5_benchmark.py
├── test_submission_15_puzzle.py
└── test_additional_confidence.py
```
