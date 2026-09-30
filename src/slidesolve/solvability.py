"""Solvability checks for sliding puzzles using inversion parity."""

from __future__ import annotations

from .board import Board, validate_board


class UnsolvablePuzzleError(ValueError):
    """Raised when a valid board cannot reach the standard goal."""


def inversion_count(board: Board) -> int:
    """Count out-of-order numbered tile pairs, ignoring the blank."""

    numbered = [tile for tile in board if tile != 0]
    return sum(
        left > right
        for index, left in enumerate(numbered)
        for right in numbered[index + 1 :]
    )


def is_solvable(board: Board, width: int | None = None) -> bool:
    """Return whether ``board`` can reach the standard goal configuration."""

    board, width = validate_board(board, width)
    inversions = inversion_count(board)

    if width % 2 == 1:
        return inversions % 2 == 0

    blank_row_from_bottom = width - (board.index(0) // width)
    return (blank_row_from_bottom + inversions) % 2 == 1

