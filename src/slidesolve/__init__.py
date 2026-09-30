"""Core types and functions for the SlideSolve puzzle solver."""

from .astar import SearchLimitExceeded, SearchResult, SearchStats, solve
from .board import (
    Board,
    BoardValidationError,
    format_board,
    goal_board,
    neighbours,
    parse_board,
    validate_board,
)
from .heuristics import manhattan, misplaced, zero
from .generator import GeneratedPuzzle, generate_puzzle
from .solvability import UnsolvablePuzzleError, inversion_count, is_solvable

__all__ = [
    "Board",
    "BoardValidationError",
    "GeneratedPuzzle",
    "SearchLimitExceeded",
    "SearchResult",
    "SearchStats",
    "UnsolvablePuzzleError",
    "format_board",
    "generate_puzzle",
    "goal_board",
    "inversion_count",
    "is_solvable",
    "manhattan",
    "misplaced",
    "neighbours",
    "parse_board",
    "solve",
    "validate_board",
    "zero",
]
