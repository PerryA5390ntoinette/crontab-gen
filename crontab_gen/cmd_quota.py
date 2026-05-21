"""CLI subcommand: quota — check how often an expression fires in a time window."""
from __future__ import annotations

import argparse
import sys

from .quota import check_quota


def add_quota_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "quota",
        help="Warn if a cron expression fires too many times in a window",
    )
    p.add_argument("expression", help="Cron expression to check")
    p.add_argument(
        "--limit",
        type=int,
        default=60,
        metavar="N",
        help="Maximum allowed firings (default: 60)",
    )
    p.add_argument(
        "--window",
        type=int,
        default=24,
        metavar="HOURS",
        dest="window_hours",
        help="Window size in hours (default: 24)",
    )
    p.set_defaults(func=cmd_quota)


def cmd_quota(args: argparse.Namespace) -> None:
    try:
        result = check_quota(
            expression=args.expression,
            limit=args.limit,
            window_hours=args.window_hours,
        )
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(result)
    if not result.ok:
        sys.exit(1)
