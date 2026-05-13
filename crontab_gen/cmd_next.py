"""CLI sub-command: next — show upcoming run times for a cron expression."""

import argparse
from datetime import datetime

from .next_run import next_runs

_DEFAULT_COUNT = 5
_DATETIME_FMT = "%Y-%m-%d %H:%M"


def add_next_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    """Register the *next* sub-command on *subparsers*."""
    parser = subparsers.add_parser(
        "next",
        help="Show the next scheduled run times for a cron expression",
    )
    parser.add_argument(
        "expression",
        help="Cron expression (quote it: '*/5 * * * *')",
    )
    parser.add_argument(
        "-n",
        "--count",
        type=int,
        default=_DEFAULT_COUNT,
        metavar="N",
        help=f"Number of upcoming runs to display (default: {_DEFAULT_COUNT})",
    )
    parser.add_argument(
        "--after",
        default=None,
        metavar="DATETIME",
        help="Start searching after this datetime (format: 'YYYY-MM-DD HH:MM')",
    )
    parser.set_defaults(func=cmd_next)


def cmd_next(args: argparse.Namespace) -> int:
    """Execute the *next* sub-command.

    Returns:
        0 on success, 1 on error.
    """
    after: datetime | None = None
    if args.after:
        try:
            after = datetime.strptime(args.after, _DATETIME_FMT)
        except ValueError:
            print(f"Error: --after must be in format 'YYYY-MM-DD HH:MM', got {args.after!r}")
            return 1

    try:
        runs = next_runs(args.expression, count=args.count, after=after)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    if not runs:
        print("No matching run times found within the search window.")
        return 0

    label = after.strftime(_DATETIME_FMT) if after else "now"
    print(f"Next {len(runs)} run(s) for '{args.expression}' (after {label}):")
    for i, dt in enumerate(runs, 1):
        print(f"  {i:>2}. {dt.strftime(_DATETIME_FMT)}")
    return 0
