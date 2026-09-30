"""A* search and optimal solution-path reconstruction."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from heapq import heappop, heappush
from itertools import count
from time import perf_counter

from .board import Board, Move, goal_board, neighbours, validate_board
from .heuristics import get_heuristic
from .solvability import UnsolvablePuzzleError, is_solvable

Heuristic = Callable[[Board, int], int]


class SearchLimitExceeded(RuntimeError):
    """Raised when a caller-selected state expansion limit is reached."""

    def __init__(self, limit: int) -> None:
        super().__init__(f"Search stopped after reaching the limit of {limit} expansions.")
        self.limit = limit


@dataclass(frozen=True, slots=True)
class SearchStats:
    """Measurements collected during one A* search."""

    expanded: int
    generated: int
    max_frontier: int
    elapsed_seconds: float


@dataclass(frozen=True, slots=True)
class SearchResult:
    """An optimal solution and the measurements used to find it."""

    boards: tuple[Board, ...]
    moves: tuple[Move, ...]
    stats: SearchStats

    @property
    def solution_length(self) -> int:
        return len(self.moves)


def solve(
    start: Board,
    *,
    width: int | None = None,
    heuristic: str | Heuristic = "manhattan",
    max_expanded: int | None = None,
) -> SearchResult:
    """Find an optimal route from ``start`` to the standard goal using A*.

    ``heuristic`` can be one of the registered names or a compatible callable.
    A custom heuristic must be admissible and zero at the goal if optimality is
    required. These conditions hold for all registered heuristics.
    """

    start, width = validate_board(start, width)
    if not is_solvable(start, width):
        raise UnsolvablePuzzleError("This board cannot reach the standard goal.")
    if max_expanded is not None and (
        not isinstance(max_expanded, int)
        or isinstance(max_expanded, bool)
        or max_expanded < 0
    ):
        raise ValueError("max_expanded must be a non-negative integer or None.")

    estimate = get_heuristic(heuristic) if isinstance(heuristic, str) else heuristic
    if not callable(estimate):
        raise TypeError("heuristic must be a registered name or callable.")

    goal = goal_board(width)
    started_at = perf_counter()
    tie_breaker = count()

    # Entries are (f, insertion order, g, board). A newer entry can supersede an
    # older one; the g_score comparison below discards the stale entry on pop.
    frontier: list[tuple[int, int, int, Board]] = []
    heappush(frontier, (estimate(start, width), next(tie_breaker), 0, start))
    g_score: dict[Board, int] = {start: 0}
    came_from: dict[Board, tuple[Board, Move]] = {}

    expanded = 0
    generated = 0
    max_frontier = 1

    while frontier:
        _, _, current_g, current = heappop(frontier)
        if current_g != g_score.get(current):
            continue

        if current == goal:
            boards, moves = _reconstruct_path(current, came_from)
            return SearchResult(
                boards=boards,
                moves=moves,
                stats=SearchStats(
                    expanded=expanded,
                    generated=generated,
                    max_frontier=max_frontier,
                    elapsed_seconds=perf_counter() - started_at,
                ),
            )

        if max_expanded is not None and expanded >= max_expanded:
            raise SearchLimitExceeded(max_expanded)

        expanded += 1
        for move, neighbour in neighbours(current, width):
            generated += 1
            tentative_g = current_g + 1
            if tentative_g >= g_score.get(neighbour, float("inf")):
                continue

            g_score[neighbour] = tentative_g
            came_from[neighbour] = (current, move)
            priority = tentative_g + estimate(neighbour, width)
            heappush(
                frontier,
                (priority, next(tie_breaker), tentative_g, neighbour),
            )

        max_frontier = max(max_frontier, len(frontier))

    # Parity checking means this should be unreachable for the standard puzzle.
    raise RuntimeError("The search frontier was exhausted without finding the goal.")


def _reconstruct_path(
    goal: Board,
    came_from: dict[Board, tuple[Board, Move]],
) -> tuple[tuple[Board, ...], tuple[Move, ...]]:
    boards = [goal]
    moves: list[Move] = []
    current = goal

    while current in came_from:
        parent, move = came_from[current]
        boards.append(parent)
        moves.append(move)
        current = parent

    boards.reverse()
    moves.reverse()
    return tuple(boards), tuple(moves)
