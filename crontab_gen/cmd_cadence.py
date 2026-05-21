"""CLI subcommand: cadence — analyse how frequently a cron expression fires."""
from __future__ import annotations

import argparse
import sys

from .cadence import analyse_cadence


def add_cadence_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "cadence",
        help="Classify how frequently a cron expression fires",
    )
    p.add_argument("expression", help="Cron expression to analyse")
    p.add_argument(
        "--sample",
        type=int,
        default=10,
        metavar="N",
        help="Number of future runs to sample (default: 10)",
    )
    p.add_argument(
        "--short",
        action="store_true",
        help="Print only the cadence label",
    )
    p.set_defaults(func=cmd_cadence)


def cmd_cadence(args: argparse.Namespace) -> None:
    try:
        result = analyse_cadence(args.expression, sample=args.sample)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.short:
        print(result.label)
    else:
        print(result)
