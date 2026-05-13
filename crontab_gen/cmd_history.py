"""CLI sub-command: history — view and manage session history."""

from __future__ import annotations

import argparse
import sys

from crontab_gen.history import add_entry, clear_history, get_history


def add_history_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "history",
        help="View or clear previously used cron expressions",
    )
    sub = parser.add_subparsers(dest="history_cmd")

    ls = sub.add_parser("list", help="List recent expressions (default)")
    ls.add_argument(
        "-n",
        "--limit",
        type=int,
        default=10,
        metavar="N",
        help="Number of entries to show (default: 10)",
    )

    sub.add_parser("clear", help="Remove all history entries")

    parser.set_defaults(func=cmd_history)


def cmd_history(args: argparse.Namespace) -> int:
    history_cmd = getattr(args, "history_cmd", None) or "list"

    if history_cmd == "clear":
        count = clear_history()
        print(f"Cleared {count} history entry/entries.")
        return 0

    # default: list
    limit = getattr(args, "limit", 10)
    entries = get_history(limit=limit)

    if not entries:
        print("No history yet. Build or validate expressions to populate history.")
        return 0

    col_expr = max(len(e.expression) for e in entries)
    col_expr = max(col_expr, 11)  # min header width
    header = f"{'EXPRESSION':<{col_expr}}  {'CREATED':<20}  DESCRIPTION"
    print(header)
    print("-" * len(header))
    for entry in entries:
        ts = entry.created_at[:19].replace("T", " ")
        print(f"{entry.expression:<{col_expr}}  {ts:<20}  {entry.description}")

    return 0
