"""Command-line interface for solving and generating sliding puzzles."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import sys

from .astar import SearchLimitExceeded, SearchResult, solve
from .board import BoardValidationError, format_board, parse_board
from .generator import generate_puzzle
from .heuristics import HEURISTICS
from .solvability import UnsolvablePuzzleError


def build_parser() -> argparse.ArgumentParser:
    """Build the public argument parser."""

    parser = argparse.ArgumentParser(
        prog="slidesolve",
        description="Solve sliding-tile puzzles optimally with A* search.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    solve_parser = commands.add_parser(
        "solve",
        help="solve a comma- or space-separated puzzle",
    )
    solve_parser.add_argument(
        "board",
        help='tile values with 0 as the blank, e.g. "1,2,3,4,0,6,7,5,8"',
    )
    solve_parser.add_argument(
        "--heuristic",
        choices=tuple(HEURISTICS),
        default="manhattan",
        help="A* heuristic to use (default: manhattan)",
    )
    solve_parser.add_argument(
        "--max-expanded",
        type=int,
        default=None,
        metavar="N",
        help="stop before expanding more than N states",
    )
    output_group = solve_parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--show-boards",
        action="store_true",
        help="print every board in the solution path",
    )
    output_group.add_argument(
        "--quiet",
        action="store_true",
        help="print only moves and compact statistics",
    )

    generate_parser = commands.add_parser(
        "generate",
        help="generate a reproducible solvable puzzle",
    )
    generate_parser.add_argument(
        "--width",
        type=int,
        default=3,
        help="board width (default: 3)",
    )
    generate_parser.add_argument(
        "--moves",
        type=int,
        default=25,
        help="legal scramble moves made from the goal (default: 25)",
    )
    generate_parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="random seed for reproducible output",
    )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return a process exit status."""

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "solve":
            return _run_solve(args)
        if args.command == "generate":
            return _run_generate(args)
    except (BoardValidationError, UnsolvablePuzzleError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    except SearchLimitExceeded as error:
        print(f"error: {error}", file=sys.stderr)
        return 3

    parser.error(f"unknown command: {args.command}")
    return 2


def _run_solve(args: argparse.Namespace) -> int:
    board, width = parse_board(args.board)
    result = solve(
        board,
        width=width,
        heuristic=args.heuristic,
        max_expanded=args.max_expanded,
    )
    _print_solution(
        result,
        width=width,
        heuristic=args.heuristic,
        show_boards=args.show_boards,
        quiet=args.quiet,
    )
    return 0


def _run_generate(args: argparse.Namespace) -> int:
    generated = generate_puzzle(width=args.width, moves=args.moves, seed=args.seed)
    compact = ",".join(str(tile) for tile in generated.board)
    seed_text = "random" if args.seed is None else str(args.seed)

    print(
        f"Generated {args.width}x{args.width} puzzle using "
        f"{args.moves} legal moves (seed: {seed_text})"
    )
    print()
    print(format_board(generated.board, args.width))
    print()
    print(f'Input: "{compact}"')
    scramble = " ".join(generated.scramble_moves) or "(none)"
    print(f"Scramble moves: {scramble}")
    return 0


def _print_solution(
    result: SearchResult,
    *,
    width: int,
    heuristic: str,
    show_boards: bool,
    quiet: bool,
) -> None:
    moves_text = " ".join(result.moves) or "(already solved)"
    stats = result.stats

    if quiet:
        print(f"moves={moves_text}")
        print(
            f"length={result.solution_length} expanded={stats.expanded} "
            f"generated={stats.generated} max_frontier={stats.max_frontier} "
            f"elapsed_seconds={stats.elapsed_seconds:.6f}"
        )
        return

    print("SlideSolve")
    print(f"Heuristic: {heuristic}")
    print()

    if show_boards:
        print("Solution path:")
        for step, board in enumerate(result.boards):
            label = "start" if step == 0 else result.moves[step - 1]
            print()
            print(f"Step {step} ({label}):")
            print(format_board(board, width))
    else:
        print("Start:")
        print(format_board(result.boards[0], width))

    print()
    print(f"Moves ({result.solution_length}): {moves_text}")
    print(f"Expanded states: {stats.expanded}")
    print(f"Generated transitions: {stats.generated}")
    print(f"Maximum frontier size: {stats.max_frontier}")
    print(f"Runtime: {stats.elapsed_seconds:.6f} seconds")

