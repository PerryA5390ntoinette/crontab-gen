"""CLI subcommand: priority — tag cron expressions by priority level."""
from __future__ import annotations

import argparse
from pathlib import Path

from crontab_gen.priority import LEVELS, add_priority, list_priorities, remove_priority
from crontab_gen.expression import is_valid


def add_priority_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("priority", help="tag expressions with a priority level")
    sub = p.add_subparsers(dest="priority_cmd", required=True)

    # add
    pa = sub.add_parser("add", help="assign a priority level to an expression")
    pa.add_argument("expression", help="cron expression")
    pa.add_argument("level", choices=LEVELS, help="priority level")
    pa.add_argument("--label", default=None, help="optional human-readable label")
    pa.add_argument("--file", default=None, help="custom storage file")

    # remove
    pr = sub.add_parser("remove", help="remove priority tag for an expression")
    pr.add_argument("expression", help="cron expression")
    pr.add_argument("--file", default=None, help="custom storage file")

    # list
    pl = sub.add_parser("list", help="list prioritised expressions")
    pl.add_argument("--level", choices=LEVELS, default=None, help="filter by level")
    pl.add_argument("--file", default=None, help="custom storage file")

    p.set_defaults(func=cmd_priority)


def cmd_priority(args: argparse.Namespace) -> None:
    kwargs = {}
    if args.file:
        kwargs["path"] = Path(args.file)

    if args.priority_cmd == "add":
        if not is_valid(args.expression):
            print(f"Error: invalid cron expression: {args.expression}")
            return
        entry = add_priority(args.expression, args.level, label=args.label, **kwargs)
        label_part = f" ({entry.label})" if entry.label else ""
        print(f"Priority '{entry.level}' set for '{entry.expression}'{label_part}.")

    elif args.priority_cmd == "remove":
        removed = remove_priority(args.expression, **kwargs)
        if removed:
            print(f"Priority tag removed for '{args.expression}'.")
        else:
            print(f"No priority tag found for '{args.expression}'.")

    elif args.priority_cmd == "list":
        entries = list_priorities(level=args.level, **kwargs)
        if not entries:
            print("No prioritised expressions found.")
            return
        for e in entries:
            label_part = f"  # {e.label}" if e.label else ""
            print(f"[{e.level:<8}] {e.expression}{label_part}")
