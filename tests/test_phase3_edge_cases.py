"""Broader correctness, property, and edge-case tests for Phase 3."""

from __future__ import annotations

from collections import deque
from itertools import permutations
import random
import unittest

from slidesolve import (
    Board,
    BoardValidationError,
    SearchLimitExceeded,
    format_board,
    goal_board,
    is_solvable,
    manhattan,
    misplaced,
    neighbours,
    parse_board,
    solve,
    validate_board,
)


def exact_distances(width: int) -> dict[Board, int]:
    """Return exact distances by breadth-first search from the goal."""

    goal = goal_board(width)
    distances = {goal: 0}
    queue = deque([goal])

    while queue:
        current = queue.popleft()
        for _, neighbour in neighbours(current, width):
            if neighbour not in distances:
                distances[neighbour] = distances[current] + 1
                queue.append(neighbour)

    return distances


def assert_legal_path(test: unittest.TestCase, boards: tuple[Board, ...], width: int) -> None:
    """Assert that every adjacent pair is connected by one legal move."""

    for current, following in zip(boards, boards[1:]):
        legal_boards = {candidate for _, candidate in neighbours(current, width)}
        test.assertIn(following, legal_boards)


class ValidationEdgeCaseTests(unittest.TestCase):
    def test_rejects_empty_board(self) -> None:
        with self.assertRaises(BoardValidationError):
            validate_board(())

    def test_rejects_one_by_one_board(self) -> None:
        with self.assertRaises(BoardValidationError):
            validate_board((0,))

    def test_rejects_non_square_tile_count(self) -> None:
        with self.assertRaises(BoardValidationError):
            validate_board((0, 1, 2))

    def test_rejects_boolean_tiles_even_though_bool_is_an_int_subclass(self) -> None:
        with self.assertRaises(BoardValidationError):
            validate_board((0, 1, 2, True), width=2)

    def test_rejects_non_integer_text(self) -> None:
        with self.assertRaises(BoardValidationError):
            parse_board("1,2,3,4,5,6,7,eight,0")

    def test_format_board_uses_visible_blank(self) -> None:
        rendered = format_board((1, 2, 3, 4, 5, 6, 7, 0, 8), 3)
        self.assertEqual(rendered, "1 2 3\n4 5 6\n7 _ 8")


class MovePropertyTests(unittest.TestCase):
    def test_corner_blank_has_two_moves(self) -> None:
        board = goal_board(3)
        self.assertEqual([move for move, _ in neighbours(board, 3)], ["up", "left"])

    def test_neighbours_preserve_all_tiles_and_change_one_swap(self) -> None:
        board = (1, 2, 3, 4, 0, 5, 6, 7, 8)
        for _, neighbour in neighbours(board, 3):
            self.assertEqual(sorted(neighbour), list(range(9)))
            changed = sum(left != right for left, right in zip(board, neighbour))
            self.assertEqual(changed, 2)

    def test_each_move_can_be_reversed(self) -> None:
        board = (1, 2, 3, 4, 0, 5, 6, 7, 8)
        for _, neighbour in neighbours(board, 3):
            reverse_destinations = {candidate for _, candidate in neighbours(neighbour, 3)}
            self.assertIn(board, reverse_destinations)


class ExhaustiveSmallPuzzleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.distances = exact_distances(2)

    def test_exactly_half_of_two_by_two_permutations_are_reachable(self) -> None:
        self.assertEqual(len(self.distances), 12)

    def test_solvability_rule_matches_all_two_by_two_permutations(self) -> None:
        for board in permutations(range(4)):
            with self.subTest(board=board):
                self.assertEqual(is_solvable(board, 2), board in self.distances)

    def test_heuristics_never_exceed_exact_distance(self) -> None:
        for board, distance in self.distances.items():
            with self.subTest(board=board):
                self.assertLessEqual(misplaced(board, 2), distance)
                self.assertLessEqual(manhattan(board, 2), distance)

    def test_heuristics_are_consistent_across_every_reachable_edge(self) -> None:
        for board in self.distances:
            for _, neighbour in neighbours(board, 2):
                with self.subTest(board=board, neighbour=neighbour):
                    self.assertLessEqual(misplaced(board, 2), 1 + misplaced(neighbour, 2))
                    self.assertLessEqual(manhattan(board, 2), 1 + manhattan(neighbour, 2))

    def test_astar_matches_exact_distance_for_every_reachable_board(self) -> None:
        for board, distance in self.distances.items():
            for heuristic in ("zero", "misplaced", "manhattan"):
                with self.subTest(board=board, heuristic=heuristic):
                    result = solve(board, width=2, heuristic=heuristic)
                    self.assertEqual(result.solution_length, distance)
                    assert_legal_path(self, result.boards, 2)


class SearchBehaviourTests(unittest.TestCase):
    def test_solution_moves_match_the_returned_board_path(self) -> None:
        start = (1, 2, 3, 4, 0, 6, 7, 5, 8)
        result = solve(start)
        self.assertEqual(len(result.boards), len(result.moves) + 1)

        for board, move, following in zip(
            result.boards, result.moves, result.boards[1:]
        ):
            transitions = dict(neighbours(board, 3))
            self.assertEqual(transitions[move], following)

    def test_zero_limit_allows_goal_but_rejects_unsolved_board(self) -> None:
        self.assertEqual(solve(goal_board(3), max_expanded=0).solution_length, 0)
        with self.assertRaises(SearchLimitExceeded):
            solve((1, 2, 3, 4, 5, 6, 7, 0, 8), max_expanded=0)

    def test_rejects_invalid_limit(self) -> None:
        with self.assertRaises(ValueError):
            solve(goal_board(3), max_expanded=-1)
        with self.assertRaises(ValueError):
            solve(goal_board(3), max_expanded=True)

    def test_rejects_unknown_heuristic(self) -> None:
        with self.assertRaises(ValueError):
            solve(goal_board(3), heuristic="magic")

    def test_seeded_random_scrambles_produce_legal_optimal_paths(self) -> None:
        generator = random.Random(20260926)
        goal = goal_board(3)

        for scramble_length in range(1, 13):
            board = goal
            previous: Board | None = None
            for _ in range(scramble_length):
                options = [
                    candidate
                    for _, candidate in neighbours(board, 3)
                    if candidate != previous
                ]
                previous, board = board, generator.choice(options)

            with self.subTest(scramble_length=scramble_length, board=board):
                baseline = solve(board, heuristic="zero")
                informed = solve(board, heuristic="manhattan")
                self.assertEqual(informed.solution_length, baseline.solution_length)
                self.assertLessEqual(informed.solution_length, scramble_length)
                self.assertEqual(informed.boards[0], board)
                self.assertEqual(informed.boards[-1], goal)
                assert_legal_path(self, informed.boards, 3)

    def test_known_depth_31_board(self) -> None:
        result = solve((8, 6, 7, 2, 5, 4, 3, 0, 1), heuristic="manhattan")
        self.assertEqual(result.solution_length, 31)
        self.assertEqual(result.boards[-1], goal_board(3))
        assert_legal_path(self, result.boards, 3)


if __name__ == "__main__":
    unittest.main()
