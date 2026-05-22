"""CLI sub-command: forecast — show upcoming fires for a cron expression."""
from __future__ import annotations

import argparse
import sys

from .forecast import build_forecast


def add_forecast_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "forecast",
        help="Show upcoming fire times for a cron expression over a time horizon",
    )
    p.add_argument("expression", help="Cron expression (quote it)")
    p.add_argument(
        "--hours",
        type=int,
        default=24,
        metavar="N",
        help="Horizon in hours (default: 24)",
    )
    p.add_argument(
        "--count-only",
        action="store_true",
        default=False,
        help="Print only the fire count",
    )
    p.set_defaults(func=cmd_forecast)


def cmd_forecast(args: argparse.Namespace) -> None:
    try:
        result = build_forecast(args.expression, horizon_hours=args.hours)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.count_only:
        print(result.count)
    else:
        print(result)
