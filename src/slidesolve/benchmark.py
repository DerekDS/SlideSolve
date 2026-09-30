"""Reproducible heuristic benchmark for the 8-puzzle solver."""

from __future__ import annotations

import argparse
from collections import deque
from collections.abc import Sequence
import csv
from dataclasses import asdict, dataclass
from pathlib import Path
import random

from .astar import solve
from .board import Board, goal_board, neighbours
from .heuristics import HEURISTICS

DEFAULT_DEPTHS = (5, 10, 15, 20, 25, 30)
DEFAULT_SEED = 20260927


@dataclass(frozen=True, slots=True)
class BenchmarkPuzzle:
    puzzle_id: str
    exact_depth: int
    board: Board


@dataclass(frozen=True, slots=True)
class BenchmarkRow:
    puzzle_id: str
    exact_depth: int
    board: str
    heuristic: str
    trial: int
    solution_length: int
    expanded: int
    generated: int
    max_frontier: int
    elapsed_seconds: float


def exact_depth_dataset(
    *,
    depths: Sequence[int] = DEFAULT_DEPTHS,
    samples_per_depth: int = 3,
    seed: int = DEFAULT_SEED,
) -> tuple[BenchmarkPuzzle, ...]:
    """Sample reproducible boards whose exact distances are known by BFS."""

    if not depths or any(depth < 0 for depth in depths):
        raise ValueError("depths must contain non-negative integers.")
    if samples_per_depth < 1:
        raise ValueError("samples_per_depth must be at least 1.")

    requested = tuple(sorted(set(depths)))
    maximum = max(requested)
    buckets: dict[int, list[Board]] = {depth: [] for depth in requested}
    goal = goal_board(3)
    queue = deque([(goal, 0)])
    seen = {goal}

    while queue:
        board, depth = queue.popleft()
        if depth in buckets:
            buckets[depth].append(board)
        if depth == maximum:
            continue

        for _, neighbour in neighbours(board, 3):
            if neighbour not in seen:
                seen.add(neighbour)
                queue.append((neighbour, depth + 1))

    chooser = random.Random(seed)
    dataset: list[BenchmarkPuzzle] = []
    for depth in requested:
        available = buckets[depth]
        if len(available) < samples_per_depth:
            raise ValueError(
                f"Depth {depth} has only {len(available)} reachable boards; "
                f"cannot sample {samples_per_depth}."
            )
        for index, board in enumerate(chooser.sample(available, samples_per_depth), 1):
            dataset.append(
                BenchmarkPuzzle(
                    puzzle_id=f"D{depth:02d}-P{index:02d}",
                    exact_depth=depth,
                    board=board,
                )
            )

    return tuple(dataset)


def run_benchmark(
    output_path: Path,
    *,
    depths: Sequence[int] = DEFAULT_DEPTHS,
    samples_per_depth: int = 3,
    repeats: int = 3,
    seed: int = DEFAULT_SEED,
) -> tuple[BenchmarkRow, ...]:
    """Run every heuristic on the same boards and write raw CSV results."""

    if repeats < 1:
        raise ValueError("repeats must be at least 1.")

    puzzles = exact_depth_dataset(
        depths=depths,
        samples_per_depth=samples_per_depth,
        seed=seed,
    )
    rows: list[BenchmarkRow] = []

    for puzzle in puzzles:
        compact_board = " ".join(str(tile) for tile in puzzle.board)
        for heuristic in HEURISTICS:
            for trial in range(1, repeats + 1):
                result = solve(puzzle.board, width=3, heuristic=heuristic)
                if result.solution_length != puzzle.exact_depth:
                    raise RuntimeError(
                        f"{puzzle.puzzle_id} expected depth {puzzle.exact_depth}, "
                        f"but {heuristic} returned {result.solution_length}."
                    )
                rows.append(
                    BenchmarkRow(
                        puzzle_id=puzzle.puzzle_id,
                        exact_depth=puzzle.exact_depth,
                        board=compact_board,
                        heuristic=heuristic,
                        trial=trial,
                        solution_length=result.solution_length,
                        expanded=result.stats.expanded,
                        generated=result.stats.generated,
                        max_frontier=result.stats.max_frontier,
                        elapsed_seconds=result.stats.elapsed_seconds,
                    )
                )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(asdict(rows[0])))
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)

    return tuple(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Benchmark SlideSolve heuristics on exact-depth 8-puzzles."
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/heuristic_comparison.csv"),
        help="CSV output path",
    )
    parser.add_argument("--samples", type=int, default=3, help="puzzles per depth")
    parser.add_argument("--repeats", type=int, default=3, help="runs per puzzle")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows = run_benchmark(
        args.output,
        samples_per_depth=args.samples,
        repeats=args.repeats,
        seed=args.seed,
    )
    puzzle_count = len({row.puzzle_id for row in rows})
    print(f"Wrote {len(rows)} runs across {puzzle_count} puzzles to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

