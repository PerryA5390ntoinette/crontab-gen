"""CLI sub-command: heatmap — show firing density across a 24-hour day."""
from __future__ import annotations

import argparse
import sys

from crontab_gen.heatmap import build_heatmap


def add_heatmap_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "heatmap",
        help="Visualise firing density of a cron expression across a 24-hour day",
    )
    p.add_argument("expression", help="Cron expression to analyse")
    p.add_argument(
        "--days",
        type=int,
        default=7,
        metavar="N",
        help="Number of days to sample (default: 7)",
    )
    p.set_defaults(func=cmd_heatmap)


def cmd_heatmap(args: argparse.Namespace) -> None:
    try:
        result = build_heatmap(args.expression, days=args.days)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(result)
