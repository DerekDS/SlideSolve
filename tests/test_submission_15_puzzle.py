"""Focused 4x4 checks added after the recorded 46-test walkthrough."""
from collections import deque
import unittest

from slidesolve import goal_board, is_solvable, solve
from test_phase4_cli import run_cli


class FifteenPuzzleTests(unittest.TestCase):
    def test_shallow_exact_distances_with_independent_moves(self):
        goal = goal_board(4)
        distances = {goal: 0}
        queue = deque([goal])
        while queue:
            board = queue.popleft()
            depth = distances[board]
            if depth == 5:
                continue
            blank = board.index(0)
            # Independent transition implementation, not slidesolve.neighbours.
            for target in range(16):
                if abs(blank // 4 - target // 4) + abs(blank % 4 - target % 4) != 1:
                    continue
                updated = list(board)
                updated[blank], updated[target] = updated[target], updated[blank]
                candidate = tuple(updated)
                if candidate not in distances:
                    distances[candidate] = depth + 1
                    queue.append(candidate)
        for board, depth in distances.items():
            for heuristic in ("zero", "misplaced", "manhattan"):
                with self.subTest(board=board, heuristic=heuristic):
                    self.assertTrue(is_solvable(board, 4))
                    result = solve(board, heuristic=heuristic, max_expanded=10000)
                    self.assertEqual(result.solution_length, depth)
                    self.assertEqual(result.boards[-1], goal)
                    for before, after in zip(result.boards, result.boards[1:]):
                        first, second = before.index(0), after.index(0)
                        self.assertEqual(abs(first // 4 - second // 4) + abs(first % 4 - second % 4), 1)
                        changed = [i for i in range(16) if before[i] != after[i]]
                        self.assertEqual(set(changed), {first, second})
                        self.assertEqual(before[second], after[first])

    def test_rejects_swapped_numbered_tiles(self):
        board = tuple(range(1, 14)) + (15, 14, 0)
        self.assertFalse(is_solvable(board, 4))
        with self.assertRaisesRegex(ValueError, "cannot reach"):
            solve(board)

    def test_rejects_user_unsolvable_example(self):
        board = (1, 2, 3, 0, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 4, 15)
        self.assertFalse(is_solvable(board, 4))

    def test_cli_solves_fifteen_puzzle(self):
        status, output, errors = run_cli(["solve", "1,2,3,4,5,6,7,8,9,10,11,12,13,0,14,15", "--show-boards", "--max-expanded", "1000"])
        self.assertEqual(status, 0)
        self.assertEqual(errors, "")
        self.assertIn("Moves (2): right right", output)
        self.assertIn("Step 2 (right):", output)


if __name__ == "__main__":
    unittest.main()
