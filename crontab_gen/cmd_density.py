"""CLI sub-command: density — analyse how densely an expression fires."""

from __future__ import annotations

import argparse

from .density import analyse_density


def add_density_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "density",
        help="Analyse the firing density of a cron expression",
    )
    parser.add_argument("expression", help="Cron expression to analyse")
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        metavar="N",
        help="Analysis window in hours (default: 24)",
    )
    parser.set_defaults(func=cmd_density)


def cmd_density(args: argparse.Namespace) -> None:
    try:
        result = analyse_density(args.expression, window_hours=args.hours)
    except ValueError as exc:
        print(f"Error: {exc}")
        return
    print(result)
