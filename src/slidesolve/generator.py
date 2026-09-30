"""Reproducible generation of solvable sliding-puzzle boards."""

from __future__ import annotations

from dataclasses import dataclass
import random

from .board import Board, Move, goal_board, neighbours


@dataclass(frozen=True, slots=True)
class GeneratedPuzzle:
    """A generated board and the legal moves used to scramble it."""

    board: Board
    scramble_moves: tuple[Move, ...]


def generate_puzzle(
    *,
    width: int = 3,
    moves: int = 25,
    seed: int | None = None,
) -> GeneratedPuzzle:
    """Scramble the goal with legal moves and return a solvable puzzle.

    Immediate reversal of the previous move is avoided. The requested number of
    scramble moves is not necessarily the board's optimal distance from the
    goal because a longer sequence can revisit a state by another route.
    """

    board = goal_board(width)  # Also validates the width.
    if not isinstance(moves, int) or isinstance(moves, bool) or moves < 0:
        raise ValueError("moves must be a non-negative integer.")

    chooser = random.Random(seed)
    previous: Board | None = None
    used_moves: list[Move] = []

    for _ in range(moves):
        options = [
            (move, candidate)
            for move, candidate in neighbours(board, width)
            if candidate != previous
        ]
        move, candidate = chooser.choice(options)
        previous, board = board, candidate
        used_moves.append(move)

    return GeneratedPuzzle(board=board, scramble_moves=tuple(used_moves))

