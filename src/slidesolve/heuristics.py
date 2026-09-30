"""Admissible heuristics for the standard sliding-puzzle goal."""

from __future__ import annotations

from collections.abc import Callable

from .board import Board

Heuristic = Callable[[Board, int], int]


def zero(board: Board, width: int) -> int:
    """Return zero, making A* behave like uniform-cost search."""

    del board, width
    return 0


def misplaced(board: Board, width: int) -> int:
    """Count numbered tiles that are not in their goal positions."""

    del width
    return sum(tile != 0 and tile != index + 1 for index, tile in enumerate(board))


def manhattan(board: Board, width: int) -> int:
    """Sum each numbered tile's grid distance from its goal position."""

    distance = 0
    for index, tile in enumerate(board):
        if tile == 0:
            continue
        current_row, current_column = divmod(index, width)
        goal_row, goal_column = divmod(tile - 1, width)
        distance += abs(current_row - goal_row) + abs(current_column - goal_column)
    return distance


HEURISTICS: dict[str, Heuristic] = {
    "zero": zero,
    "misplaced": misplaced,
    "manhattan": manhattan,
}


def get_heuristic(name: str) -> Heuristic:
    """Resolve a public heuristic name or raise a useful error."""

    try:
        return HEURISTICS[name]
    except KeyError as error:
        choices = ", ".join(sorted(HEURISTICS))
        raise ValueError(f"Unknown heuristic {name!r}. Choose one of: {choices}.") from error

