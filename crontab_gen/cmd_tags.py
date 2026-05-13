"""CLI subcommand for managing expression tags."""
from __future__ import annotations

import argparse
import sys

from crontab_gen.tags import add_tag, remove_tag, find_by_tag, list_tags


def add_tags_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("tags", help="Manage tags for cron expressions")
    sub = parser.add_subparsers(dest="tags_cmd", required=True)

    # add
    p_add = sub.add_parser("add", help="Tag a cron expression")
    p_add.add_argument("expression", help="Cron expression to tag")
    p_add.add_argument("tags", nargs="+", help="One or more tags")
    p_add.add_argument("--note", default=None, help="Optional note")

    # remove
    p_rm = sub.add_parser("remove", help="Remove tags from an expression")
    p_rm.add_argument("expression", help="Cron expression")
    p_rm.add_argument("tags", nargs="+", help="Tags to remove")

    # find
    p_find = sub.add_parser("find", help="Find expressions by tag")
    p_find.add_argument("tag", help="Tag to search for")

    # list
    sub.add_parser("list", help="List all tagged expressions")

    parser.set_defaults(func=cmd_tags)


def cmd_tags(args: argparse.Namespace) -> None:
    if args.tags_cmd == "add":
        entry = add_tag(args.expression, args.tags, note=args.note)
        print(f"Tagged '{entry.expression}' with: {', '.join(entry.tags)}")
        if entry.note:
            print(f"  Note: {entry.note}")

    elif args.tags_cmd == "remove":
        entry = remove_tag(args.expression, args.tags)
        if entry is None:
            print(f"No tags found for '{args.expression}'.")
            sys.exit(1)
        remaining = ", ".join(entry.tags) if entry.tags else "(none)"
        print(f"Updated tags for '{entry.expression}': {remaining}")

    elif args.tags_cmd == "find":
        results = find_by_tag(args.tag)
        if not results:
            print(f"No expressions tagged with '{args.tag}'.")
        else:
            for e in results:
                note_str = f"  # {e.note}" if e.note else ""
                print(f"{e.expression}  [{', '.join(e.tags)}]{note_str}")

    elif args.tags_cmd == "list":
        entries = list_tags()
        if not entries:
            print("No tagged expressions.")
        else:
            for e in entries:
                note_str = f"  # {e.note}" if e.note else ""
                print(f"{e.expression}  [{', '.join(e.tags)}]{note_str}")
