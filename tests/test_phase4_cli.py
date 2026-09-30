"""Tests for puzzle generation and the public command-line interface."""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import unittest

from slidesolve import generate_puzzle, goal_board, is_solvable, neighbours
from slidesolve.cli import main


def run_cli(arguments: list[str]) -> tuple[int, str, str]:
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        status = main(arguments)
    return status, stdout.getvalue(), stderr.getvalue()


class GeneratorTests(unittest.TestCase):
    def test_same_seed_produces_same_puzzle(self) -> None:
        first = generate_puzzle(width=3, moves=25, seed=42)
        second = generate_puzzle(width=3, moves=25, seed=42)
        self.assertEqual(first, second)

    def test_generated_puzzle_is_solvable_and_moves_are_legal(self) -> None:
        generated = generate_puzzle(width=3, moves=30, seed=7)
        self.assertTrue(is_solvable(generated.board, 3))

        board = goal_board(3)
        for move in generated.scramble_moves:
            transitions = dict(neighbours(board, 3))
            self.assertIn(move, transitions)
            board = transitions[move]
        self.assertEqual(board, generated.board)

    def test_zero_moves_returns_goal(self) -> None:
        generated = generate_puzzle(width=3, moves=0, seed=1)
        self.assertEqual(generated.board, goal_board(3))
        self.assertEqual(generated.scramble_moves, ())

    def test_rejects_invalid_generation_arguments(self) -> None:
        with self.assertRaises(ValueError):
            generate_puzzle(width=1, moves=5)
        with self.assertRaises(ValueError):
            generate_puzzle(width=3, moves=-1)


class SolveCommandTests(unittest.TestCase):
    def test_solves_and_prints_statistics(self) -> None:
        status, output, errors = run_cli(
            ["solve", "1,2,3,4,0,6,7,5,8", "--heuristic", "manhattan"]
        )
        self.assertEqual(status, 0)
        self.assertEqual(errors, "")
        self.assertIn("Moves (2): down right", output)
        self.assertIn("Expanded states:", output)
        self.assertIn("Runtime:", output)

    def test_show_boards_prints_each_step(self) -> None:
        status, output, _ = run_cli(
            ["solve", "1,2,3,4,0,6,7,5,8", "--show-boards"]
        )
        self.assertEqual(status, 0)
        self.assertIn("Step 0 (start):", output)
        self.assertIn("Step 1 (down):", output)
        self.assertIn("Step 2 (right):", output)

    def test_quiet_output_is_compact(self) -> None:
        status, output, _ = run_cli(
            ["solve", "1,2,3,4,5,6,7,0,8", "--quiet"]
        )
        self.assertEqual(status, 0)
        self.assertTrue(output.startswith("moves=right\nlength=1 "))
        self.assertNotIn("SlideSolve", output)

    def test_invalid_board_has_clear_error_and_status_two(self) -> None:
        status, output, errors = run_cli(["solve", "1,2,3,4,5,6,7,7,0"])
        self.assertEqual(status, 2)
        self.assertEqual(output, "")
        self.assertIn("error:", errors)
        self.assertIn("exactly once", errors)

    def test_unsolvable_board_has_clear_error(self) -> None:
        status, _, errors = run_cli(["solve", "1,2,3,4,5,6,8,7,0"])
        self.assertEqual(status, 2)
        self.assertIn("cannot reach", errors)

    def test_search_limit_has_distinct_status(self) -> None:
        status, _, errors = run_cli(
            ["solve", "1,2,3,4,5,6,7,0,8", "--max-expanded", "0"]
        )
        self.assertEqual(status, 3)
        self.assertIn("limit of 0 expansions", errors)


class GenerateCommandTests(unittest.TestCase):
    def test_generate_prints_reusable_input(self) -> None:
        status, output, errors = run_cli(
            ["generate", "--moves", "10", "--seed", "42"]
        )
        self.assertEqual(status, 0)
        self.assertEqual(errors, "")
        self.assertIn("Generated 3x3 puzzle", output)
        self.assertIn("seed: 42", output)
        self.assertIn('Input: "', output)
        self.assertIn("Scramble moves:", output)

    def test_generate_reports_bad_width(self) -> None:
        status, output, errors = run_cli(["generate", "--width", "1"])
        self.assertEqual(status, 2)
        self.assertEqual(output, "")
        self.assertIn("width", errors)


if __name__ == "__main__":
    unittest.main()
