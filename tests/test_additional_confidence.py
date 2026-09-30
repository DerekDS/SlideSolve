"""High-confidence state-space and 15-puzzle generation checks."""

from __future__ import annotations

from collections import deque
import unittest

from slidesolve import generate_puzzle, goal_board, is_solvable, solve
from slidesolve.heuristics import manhattan, misplaced


Board = tuple[int, ...]


def independent_neighbours(board: Board, width: int):
    """Yield legal blank moves without using the production move generator."""

    blank = board.index(0)
    row, column = divmod(blank, width)
    for move, row_delta, column_delta in (
        ("up", -1, 0),
        ("down", 1, 0),
        ("left", 0, -1),
        ("right", 0, 1),
    ):
        new_row = row + row_delta
        new_column = column + column_delta
        if not (0 <= new_row < width and 0 <= new_column < width):
            continue
        target = new_row * width + new_column
        updated = list(board)
        updated[blank], updated[target] = updated[target], updated[blank]
        yield move, tuple(updated)


class IndependentEightPuzzleOracleTests(unittest.TestCase):
    """Compare production behaviour with a complete independent 3x3 BFS."""

    @classmethod
    def setUpClass(cls) -> None:
        goal = goal_board(3)
        cls.distances = {goal: 0}
        cls.representatives = {0: goal}
        queue = deque([goal])

        while queue:
            board = queue.popleft()
            next_depth = cls.distances[board] + 1
            for _, candidate in independent_neighbours(board, 3):
                if candidate in cls.distances:
                    continue
                cls.distances[candidate] = next_depth
                cls.representatives.setdefault(next_depth, candidate)
                queue.append(candidate)

    def assert_independent_path_is_legal(self, result) -> None:
        self.assertEqual(len(result.boards), len(result.moves) + 1)
        for before, move, after in zip(
            result.boards, result.moves, result.boards[1:]
        ):
            transitions = dict(independent_neighbours(before, 3))
            self.assertIn(move, transitions)
            self.assertEqual(transitions[move], after)

    def test_oracle_contains_complete_reachable_state_space(self) -> None:
        self.assertEqual(len(self.distances), 181_440)
        self.assertEqual(set(self.representatives), set(range(32)))
        self.assertEqual(max(self.distances.values()), 31)

    def test_solvability_matches_every_reachable_board_and_its_twin(self) -> None:
        for board in self.distances:
            self.assertTrue(is_solvable(board, 3))
            twin = list(board)
            first = twin.index(1)
            second = twin.index(2)
            twin[first], twin[second] = twin[second], twin[first]
            self.assertFalse(is_solvable(tuple(twin), 3))

    def test_heuristics_are_admissible_and_consistent_everywhere(self) -> None:
        for board, distance in self.distances.items():
            for heuristic in (misplaced, manhattan):
                estimate = heuristic(board, 3)
                self.assertLessEqual(estimate, distance)
                for _, candidate in independent_neighbours(board, 3):
                    self.assertLessEqual(estimate, 1 + heuristic(candidate, 3))

    def test_manhattan_astar_matches_an_oracle_board_at_every_depth(self) -> None:
        for depth, board in self.representatives.items():
            with self.subTest(depth=depth):
                result = solve(board, heuristic="manhattan")
                self.assertEqual(result.solution_length, depth)
                self.assertEqual(result.boards[-1], goal_board(3))
                self.assert_independent_path_is_legal(result)

    def test_all_heuristics_match_oracle_across_the_depth_range(self) -> None:
        for depth in (0, 5, 10, 15, 20, 25, 30, 31):
            board = self.representatives[depth]
            for heuristic in ("zero", "misplaced", "manhattan"):
                with self.subTest(depth=depth, heuristic=heuristic):
                    result = solve(board, heuristic=heuristic)
                    self.assertEqual(result.solution_length, depth)
                    self.assert_independent_path_is_legal(result)


class FifteenPuzzleGenerationPropertyTests(unittest.TestCase):
    def test_many_seeded_scrambles_are_valid_solvable_and_replayable(self) -> None:
        for seed in range(20):
            for move_count in (0, 1, 2, 10, 50):
                with self.subTest(seed=seed, move_count=move_count):
                    generated = generate_puzzle(
                        width=4,
                        moves=move_count,
                        seed=seed,
                    )
                    self.assertEqual(len(generated.scramble_moves), move_count)
                    self.assertEqual(set(generated.board), set(range(16)))
                    self.assertTrue(is_solvable(generated.board, 4))

                    board = goal_board(4)
                    previous = None
                    for move in generated.scramble_moves:
                        transitions = dict(independent_neighbours(board, 4))
                        self.assertIn(move, transitions)
                        candidate = transitions[move]
                        if previous is not None:
                            self.assertNotEqual(candidate, previous)
                        previous, board = board, candidate

                    self.assertEqual(board, generated.board)


if __name__ == "__main__":
    unittest.main()
