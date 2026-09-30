"""Tests for the reproducible heuristic benchmark."""

from __future__ import annotations

import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from slidesolve.benchmark import exact_depth_dataset, run_benchmark


class DatasetTests(unittest.TestCase):
    def test_dataset_is_reproducible_and_has_requested_depths(self) -> None:
        first = exact_depth_dataset(depths=(0, 1, 5), samples_per_depth=1, seed=12)
        second = exact_depth_dataset(depths=(0, 1, 5), samples_per_depth=1, seed=12)
        self.assertEqual(first, second)
        self.assertEqual([puzzle.exact_depth for puzzle in first], [0, 1, 5])

    def test_rejects_more_samples_than_a_depth_contains(self) -> None:
        with self.assertRaises(ValueError):
            exact_depth_dataset(depths=(0,), samples_per_depth=2)


class BenchmarkTests(unittest.TestCase):
    def test_writes_one_row_per_puzzle_heuristic_and_trial(self) -> None:
        with TemporaryDirectory() as directory:
            output = Path(directory) / "results.csv"
            rows = run_benchmark(
                output,
                depths=(1, 3),
                samples_per_depth=1,
                repeats=2,
                seed=7,
            )
            self.assertEqual(len(rows), 2 * 3 * 2)
            self.assertTrue(output.exists())

            with output.open(newline="", encoding="utf-8") as source:
                written = list(csv.DictReader(source))
            self.assertEqual(len(written), len(rows))
            self.assertEqual(
                {row["heuristic"] for row in written},
                {"zero", "misplaced", "manhattan"},
            )
            self.assertTrue(
                all(row["exact_depth"] == row["solution_length"] for row in written)
            )


if __name__ == "__main__":
    unittest.main()
