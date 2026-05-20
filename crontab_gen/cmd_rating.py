"""CLI subcommand: rating — rate cron expressions 1-5."""
from __future__ import annotations

import argparse
from pathlib import Path

from crontab_gen.expression import is_valid
from crontab_gen.rating import add_rating, get_rating, list_ratings, remove_rating

_DEFAULT_PATH = Path.home() / ".crontab_gen" / "ratings.json"


def add_rating_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("rating", help="Rate cron expressions (1-5)")
    sub = p.add_subparsers(dest="rating_cmd", required=True)

    # rate
    rate_p = sub.add_parser("rate", help="Assign a score to an expression")
    rate_p.add_argument("expression", help="Cron expression")
    rate_p.add_argument("score", type=int, help="Score from 1 to 5")
    rate_p.add_argument("--label", default=None, help="Optional label")
    rate_p.add_argument("--file", type=Path, default=_DEFAULT_PATH)

    # show
    show_p = sub.add_parser("show", help="Show rating for an expression")
    show_p.add_argument("expression", help="Cron expression")
    show_p.add_argument("--file", type=Path, default=_DEFAULT_PATH)

    # list
    list_p = sub.add_parser("list", help="List all rated expressions")
    list_p.add_argument("--file", type=Path, default=_DEFAULT_PATH)
    list_p.add_argument("--min-score", type=int, default=1, dest="min_score")

    # remove
    rm_p = sub.add_parser("remove", help="Remove rating for an expression")
    rm_p.add_argument("expression", help="Cron expression")
    rm_p.add_argument("--file", type=Path, default=_DEFAULT_PATH)

    p.set_defaults(func=cmd_rating)


def cmd_rating(args: argparse.Namespace) -> None:
    if args.rating_cmd == "rate":
        if not is_valid(args.expression):
            print(f"Error: '{args.expression}' is not a valid cron expression.")
            return
        try:
            entry = add_rating(args.expression, args.score, args.label, args.file)
        except ValueError as exc:
            print(f"Error: {exc}")
            return
        label_part = f" ({entry.label})" if entry.label else ""
        print(f"Rated '{entry.expression}'{label_part}: {entry.score}/5")

    elif args.rating_cmd == "show":
        entry = get_rating(args.expression, args.file)
        if entry is None:
            print(f"No rating found for '{args.expression}'.")
        else:
            label_part = f" — {entry.label}" if entry.label else ""
            print(f"{entry.expression}{label_part}: {entry.score}/5")

    elif args.rating_cmd == "list":
        entries = [e for e in list_ratings(args.file) if e.score >= args.min_score]
        if not entries:
            print("No ratings found.")
            return
        entries.sort(key=lambda e: e.score, reverse=True)
        for e in entries:
            label_part = f"  {e.label}" if e.label else ""
            print(f"{e.score}/5  {e.expression}{label_part}")

    elif args.rating_cmd == "remove":
        removed = remove_rating(args.expression, args.file)
        if removed:
            print(f"Removed rating for '{args.expression}'.")
        else:
            print(f"No rating found for '{args.expression}'.")
