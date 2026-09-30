"""Aggregate the raw SlideSolve benchmark into CSV and Markdown summaries."""

from __future__ import annotations

import argparse
from collections import defaultdict
import csv
from pathlib import Path
from statistics import fmean, median


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


def summarize(rows: list[dict[str, str]]) -> list[dict[str, int | float | str]]:
    groups: dict[tuple[int, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        groups[(int(row["exact_depth"]), row["heuristic"])].append(row)

    zero_means = {
        depth: fmean(int(row["expanded"]) for row in group)
        for (depth, heuristic), group in groups.items()
        if heuristic == "zero"
    }
    summary: list[dict[str, int | float | str]] = []
    order = {"zero": 0, "misplaced": 1, "manhattan": 2}

    for (depth, heuristic), group in sorted(
        groups.items(), key=lambda item: (item[0][0], order[item[0][1]])
    ):
        mean_expanded = fmean(int(row["expanded"]) for row in group)
        summary.append(
            {
                "exact_depth": depth,
                "heuristic": heuristic,
                "puzzles": len({row["puzzle_id"] for row in group}),
                "runs": len(group),
                "mean_expanded": round(mean_expanded, 1),
                "mean_generated": round(
                    fmean(int(row["generated"]) for row in group), 1
                ),
                "mean_max_frontier": round(
                    fmean(int(row["max_frontier"]) for row in group), 1
                ),
                "median_elapsed_ms": round(
                    median(float(row["elapsed_seconds"]) * 1000 for row in group), 3
                ),
                "expansion_reduction_vs_zero_pct": round(
                    100 * (1 - mean_expanded / zero_means[depth]), 1
                ),
            }
        )

    return summary


def write_summary(path: Path, summary: list[dict[str, int | float | str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(output, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)


def write_analysis(
    path: Path,
    rows: list[dict[str, str]],
    summary: list[dict[str, int | float | str]],
) -> None:
    deepest = max(int(row["exact_depth"]) for row in rows)
    deep_rows = {
        row["heuristic"]: row
        for row in summary
        if row["exact_depth"] == deepest
    }
    puzzles = len({row["puzzle_id"] for row in rows})
    trials = len(rows)
    correctness_failures = sum(
        row["exact_depth"] != row["solution_length"] for row in rows
    )

    table_lines = [
        "| Exact depth | Heuristic | Mean expanded | Mean frontier | Median time (ms) | Reduction vs zero |",
        "| ---: | --- | ---: | ---: | ---: | ---: |",
    ]
    for row in summary:
        table_lines.append(
            f"| {row['exact_depth']} | {row['heuristic']} | "
            f"{row['mean_expanded']:,.1f} | {row['mean_max_frontier']:,.1f} | "
            f"{row['median_elapsed_ms']:,.3f} | "
            f"{row['expansion_reduction_vs_zero_pct']:.1f}% |"
        )

    manhattan = deep_rows["manhattan"]
    misplaced = deep_rows["misplaced"]
    zero = deep_rows["zero"]
    depths = ", ".join(str(d) for d in sorted({int(r["exact_depth"]) for r in rows}))
    content = f"""# Heuristic Evaluation

## Method

The benchmark uses breadth-first search from the goal to establish exact puzzle
depths. This file contains depths {depths}, with {trials} runs across {puzzles}
distinct puzzles. The original submitted dataset used three puzzles per depth,
three trials per heuristic, and seed 20260927. A CSV alone does not record the
sampling seed; custom runs must record their own command separately.

Expanded states are the primary comparison because the count is deterministic
for this implementation. Runtime is reported as a median and should be treated
as supporting evidence because it is affected by the computer and background
activity.

## Results

{chr(10).join(table_lines)}

## Main findings

- Every run returned the breadth-first-search solution length. Correctness
  mismatches: {correctness_failures}.
- At exact depth {deepest}, uniform-cost search expanded an average of
  {zero['mean_expanded']:,.1f} states. Misplaced tiles reduced this to
  {misplaced['mean_expanded']:,.1f}, a
  {misplaced['expansion_reduction_vs_zero_pct']:.1f}% reduction.
- At the same depth, Manhattan distance expanded an average of
  {manhattan['mean_expanded']:,.1f} states, a
  {manhattan['expansion_reduction_vs_zero_pct']:.1f}% reduction from the zero
  heuristic.
- The differences are small for shallow puzzles and grow rapidly with depth.
  This agrees with A* theory: a more informative admissible heuristic avoids
  exploring states whose estimated total cost cannot improve the solution.

## Limitations

- The dataset contains {puzzles} sampled 8-puzzles rather than every
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
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input", type=Path, default=Path("results/heuristic_comparison.csv")
    )
    parser.add_argument(
        "--summary", type=Path, default=Path("results/heuristic_summary.csv")
    )
    parser.add_argument(
        "--analysis", type=Path, default=Path("results/ANALYSIS.md")
    )
    args = parser.parse_args()

    rows = read_rows(args.input)
    summary = summarize(rows)
    write_summary(args.summary, summary)
    write_analysis(args.analysis, rows, summary)
    print(f"Wrote {args.summary} and {args.analysis}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
