"""CLI sub-command: conflict — detect scheduling conflicts between cron expressions."""
from __future__ import annotations

import argparse

from .conflict import detect_conflicts


def add_conflict_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "conflict",
        help="Detect scheduling conflicts between multiple cron expressions",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Two or more cron expressions to compare",
    )
    p.add_argument(
        "--horizon",
        type=int,
        default=60,
        metavar="N",
        help="Number of upcoming runs to sample per expression (default: 60)",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        default=False,
        help="Exit with non-zero status if conflicts found, print nothing",
    )
    p.set_defaults(func=cmd_conflict)


def cmd_conflict(args: argparse.Namespace) -> None:
    if len(args.expressions) < 2:
        print("Error: at least two expressions are required.")
        raise SystemExit(1)

    try:
        result = detect_conflicts(args.expressions, horizon=args.horizon)
    except ValueError as exc:
        print(f"Error: {exc}")
        raise SystemExit(1)

    if args.quiet:
        raise SystemExit(1 if result.has_conflicts else 0)

    if not result.has_conflicts:
        print("No conflicts detected.")
        return

    for pair in result.pairs:
        print(f"CONFLICT: '{pair.expr_a}' vs '{pair.expr_b}'")
        preview = pair.shared_times[:5]
        for t in preview:
            print(f"  {t}")
        if len(pair.shared_times) > 5:
            print(f"  ... and {len(pair.shared_times) - 5} more")
