"""Board representation, validation, parsing, and legal move generation."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from math import isqrt
import re

Board = tuple[int, ...]
Move = str


class BoardValidationError(ValueError):
    """Raised when a board is not a valid square sliding puzzle."""


def validate_board(values: Iterable[int], width: int | None = None) -> tuple[Board, int]:
    """Return an immutable board and its width after validating every tile.

    A valid width-w board contains each integer from 0 through w*w - 1 exactly
    once. If ``width`` is omitted, it is inferred from the number of tiles.
    """

    board = tuple(values)
    if not board:
        raise BoardValidationError("A board must contain at least one tile.")

    if any(not isinstance(tile, int) or isinstance(tile, bool) for tile in board):
        raise BoardValidationError("Every tile must be an integer.")

    if width is None:
        width = isqrt(len(board))
        if width * width != len(board):
            raise BoardValidationError(
                f"The tile count ({len(board)}) does not form a square board."
            )
        if width < 2:
            raise BoardValidationError("The board width must be at least 2.")
    elif not isinstance(width, int) or isinstance(width, bool) or width < 2:
        raise BoardValidationError("The board width must be an integer of at least 2.")
    elif len(board) != width * width:
        raise BoardValidationError(
            f"A {width}x{width} board requires {width * width} tiles, "
            f"but {len(board)} were supplied."
        )

    expected = set(range(width * width))
    actual = set(board)
    if actual != expected or len(board) != len(actual):
        missing = sorted(expected - actual)
        unexpected = sorted(actual - expected)
        duplicates = sorted({tile for tile in board if board.count(tile) > 1})
        details: list[str] = []
        if missing:
            details.append(f"missing {missing}")
        if unexpected:
            details.append(f"unexpected {unexpected}")
        if duplicates:
            details.append(f"duplicated {duplicates}")
        suffix = "; ".join(details) or "incorrect tile values"
        raise BoardValidationError(
            f"Tiles must contain every integer from 0 to {width * width - 1} "
            f"exactly once ({suffix})."
        )

    return board, width


def parse_board(text: str) -> tuple[Board, int]:
    """Parse a comma- or whitespace-separated board and validate it."""

    tokens = [token for token in re.split(r"[\s,]+", text.strip()) if token]
    if not tokens:
        raise BoardValidationError("No tile values were supplied.")
    try:
        values = [int(token) for token in tokens]
    except ValueError as error:
        raise BoardValidationError("Tile values must be integers.") from error
    return validate_board(values)


def goal_board(width: int) -> Board:
    """Return the standard goal board for ``width``."""

    if not isinstance(width, int) or isinstance(width, bool) or width < 2:
        raise BoardValidationError("The board width must be an integer of at least 2.")
    return tuple(range(1, width * width)) + (0,)


def neighbours(board: Board, width: int) -> Iterator[tuple[Move, Board]]:
    """Yield legal blank moves in deterministic up, down, left, right order.

    The caller is expected to pass a board already checked by
    :func:`validate_board`. Move names describe the blank's movement.
    """

    blank = board.index(0)
    row, column = divmod(blank, width)
    candidates = (
        ("up", row - 1, column),
        ("down", row + 1, column),
        ("left", row, column - 1),
        ("right", row, column + 1),
    )

    for move, new_row, new_column in candidates:
        if 0 <= new_row < width and 0 <= new_column < width:
            swap_index = new_row * width + new_column
            mutable = list(board)
            mutable[blank], mutable[swap_index] = mutable[swap_index], mutable[blank]
            yield move, tuple(mutable)


def format_board(board: Board, width: int) -> str:
    """Format a board for readable terminal output."""

    cell_width = max(1, len(str(width * width - 1)))
    rows: list[str] = []
    for start in range(0, len(board), width):
        cells = (
            "_".rjust(cell_width) if tile == 0 else str(tile).rjust(cell_width)
            for tile in board[start : start + width]
        )
        rows.append(" ".join(cells))
    return "\n".join(rows)
