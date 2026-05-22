"""CLI subcommand: spike — detect unusual firing bursts in a cron expression."""
from __future__ import annotations

import argparse
import sys

from .spike import detect_spike


def add_spike_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "spike",
        help="Detect firing spikes in a cron expression",
    )
    p.add_argument("expression", help="Cron expression to analyse")
    p.add_argument(
        "--window",
        type=int,
        default=60,
        metavar="MINUTES",
        help="Rolling window in minutes (default: 60)",
    )
    p.add_argument(
        "--threshold",
        type=int,
        default=10,
        metavar="N",
        help="Maximum allowed fires within the window (default: 10)",
    )
    p.set_defaults(func=cmd_spike)


def cmd_spike(args: argparse.Namespace) -> None:
    try:
        result = detect_spike(
            expression=args.expression,
            window_minutes=args.window,
            threshold=args.threshold,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(result)
    if not result.ok():
        sys.exit(2)
