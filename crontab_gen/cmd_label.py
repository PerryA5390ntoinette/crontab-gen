"""CLI subcommand: label — attach human-readable labels to cron expressions."""
from __future__ import annotations

import argparse
import sys

from crontab_gen.label import add_label, find_label, list_labels, remove_label
from crontab_gen.expression import is_valid


def add_label_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("label", help="Attach labels to cron expressions")
    sub = parser.add_subparsers(dest="label_cmd")

    # add
    p_add = sub.add_parser("add", help="Add a label for an expression")
    p_add.add_argument("expression", help="Cron expression")
    p_add.add_argument("label", help="Human-readable label")

    # remove
    p_rm = sub.add_parser("remove", help="Remove label for an expression")
    p_rm.add_argument("expression", help="Cron expression")

    # list
    sub.add_parser("list", help="List all labelled expressions")

    # show
    p_show = sub.add_parser("show", help="Show label for an expression")
    p_show.add_argument("expression", help="Cron expression")

    parser.set_defaults(func=cmd_label)


def cmd_label(args: argparse.Namespace) -> None:
    cmd = getattr(args, "label_cmd", None)

    if cmd == "add":
        if not is_valid(args.expression):
            print(f"Error: invalid cron expression: {args.expression}", file=sys.stderr)
            sys.exit(1)
        entry = add_label(args.expression, args.label)
        print(f"Labelled '{entry.expression}' as '{entry.label}'")

    elif cmd == "remove":
        removed = remove_label(args.expression)
        if removed:
            print(f"Removed label for '{args.expression}'")
        else:
            print(f"No label found for '{args.expression}'", file=sys.stderr)
            sys.exit(1)

    elif cmd == "list":
        entries = list_labels()
        if not entries:
            print("No labels saved.")
            return
        for e in entries:
            print(f"{e.expression:<30} {e.label}")

    elif cmd == "show":
        entry = find_label(args.expression)
        if entry is None:
            print(f"No label found for '{args.expression}'", file=sys.stderr)
            sys.exit(1)
        print(f"{entry.expression}: {entry.label}")

    else:
        print("Usage: crontab-gen label <add|remove|list|show>", file=sys.stderr)
        sys.exit(1)
