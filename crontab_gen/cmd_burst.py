"""CLI subcommand: burst — detect high-frequency firing within a short window."""
from __future__ import annotations

import argparse
import sys

from .burst import detect_burst


def add_burst_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "burst",
        help="Detect expressions that fire too many times in a short window",
    )
    p.add_argument("expression", help="Cron expression to analyse")
    p.add_argument(
        "--window",
        type=int,
        default=60,
        metavar="MINUTES",
        help="Time window in minutes (default: 60)",
    )
    p.add_argument(
        "--threshold",
        type=int,
        default=10,
        metavar="N",
        help="Maximum allowed fires within the window (default: 10)",
    )
    p.set_defaults(func=cmd_burst)


def cmd_burst(args: argparse.Namespace) -> None:
    try:
        result = detect_burst(
            expression=args.expression,
            window_minutes=args.window,
            threshold=args.threshold,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(result)
    if not result.ok:
        sys.exit(1)
