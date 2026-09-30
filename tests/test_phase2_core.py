"""Focused checks for the Phase 2 solver core."""

from __future__ import annotations

import unittest

from slidesolve import (
    BoardValidationError,
    UnsolvablePuzzleError,
    goal_board,
    is_solvable,
    manhattan,
    misplaced,
    neighbours,
    parse_board,
    solve,
)


class BoardTests(unittest.TestCase):
    def test_parses_commas_and_whitespace(self) -> None:
        board, width = parse_board("1,2,3 4,5,6 7,8,0")
        self.assertEqual(board, goal_board(3))
        self.assertEqual(width, 3)

    def test_rejects_duplicate_and_missing_tile(self) -> None:
        with self.assertRaises(BoardValidationError):
            parse_board("1,2,3,4,5,6,7,7,0")

    def test_centre_blank_has_four_legal_neighbours(self) -> None:
        board = (1, 2, 3, 4, 0, 6, 7, 5, 8)
        self.assertEqual(
            [move for move, _ in neighbours(board, 3)],
            ["up", "down", "left", "right"],
        )


class HeuristicTests(unittest.TestCase):
    def test_goal_estimates_are_zero(self) -> None:
        goal = goal_board(3)
        self.assertEqual(misplaced(goal, 3), 0)
        self.assertEqual(manhattan(goal, 3), 0)

    def test_blank_is_excluded(self) -> None:
        one_move = (1, 2, 3, 4, 5, 6, 7, 0, 8)
        self.assertEqual(misplaced(one_move, 3), 1)
        self.assertEqual(manhattan(one_move, 3), 1)


class SolvabilityTests(unittest.TestCase):
    def test_detects_solvable_and_unsolvable_boards(self) -> None:
        self.assertTrue(is_solvable((1, 2, 3, 4, 5, 6, 7, 0, 8), 3))
        self.assertFalse(is_solvable((1, 2, 3, 4, 5, 6, 8, 7, 0), 3))

    def test_even_width_goal_is_solvable(self) -> None:
        self.assertTrue(is_solvable(goal_board(4), 4))


class SearchTests(unittest.TestCase):
    def test_already_solved(self) -> None:
        result = solve(goal_board(3))
        self.assertEqual(result.solution_length, 0)
        self.assertEqual(result.boards, (goal_board(3),))
        self.assertEqual(result.stats.expanded, 0)

    def test_known_two_move_solution(self) -> None:
        start = (1, 2, 3, 4, 0, 6, 7, 5, 8)
        result = solve(start)
        self.assertEqual(result.moves, ("down", "right"))
        self.assertEqual(result.solution_length, 2)
        self.assertEqual(result.boards[0], start)
        self.assertEqual(result.boards[-1], goal_board(3))

    def test_heuristics_find_same_optimal_length(self) -> None:
        start = (1, 3, 6, 5, 0, 2, 4, 7, 8)
        lengths = {
            solve(start, heuristic=name).solution_length
            for name in ("zero", "misplaced", "manhattan")
        }
        self.assertEqual(len(lengths), 1)

    def test_unsolvable_board_is_rejected_before_search(self) -> None:
        with self.assertRaises(UnsolvablePuzzleError):
            solve((1, 2, 3, 4, 5, 6, 8, 7, 0))


if __name__ == "__main__":
    unittest.main()
