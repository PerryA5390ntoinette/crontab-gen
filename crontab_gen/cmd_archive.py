"""CLI subcommand: archive — manage archived cron expressions."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from crontab_gen.archive import (
    _DEFAULT_PATH,
    archive_expression,
    clear_archive,
    list_archive,
    remove_from_archive,
)


def add_archive_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("archive", help="Manage archived cron expressions")
    sub = parser.add_subparsers(dest="archive_cmd", required=True)

    # add
    p_add = sub.add_parser("add", help="Archive a cron expression")
    p_add.add_argument("expression", help="Cron expression to archive")
    p_add.add_argument("--label", default=None, help="Optional label")
    p_add.add_argument("--source", default=None, help="Origin of the expression")
    p_add.add_argument("--file", default=None, help="Custom archive file path")

    # list
    p_list = sub.add_parser("list", help="List archived expressions")
    p_list.add_argument("--file", default=None, help="Custom archive file path")

    # remove
    p_remove = sub.add_parser("remove", help="Remove a specific expression from archive")
    p_remove.add_argument("expression", help="Expression to remove")
    p_remove.add_argument("--file", default=None, help="Custom archive file path")

    # clear
    p_clear = sub.add_parser("clear", help="Clear all archived expressions")
    p_clear.add_argument("--file", default=None, help="Custom archive file path")

    parser.set_defaults(func=cmd_archive)


def cmd_archive(args: argparse.Namespace) -> None:
    path = Path(args.file) if getattr(args, "file", None) else _DEFAULT_PATH

    if args.archive_cmd == "add":
        entry = archive_expression(
            expression=args.expression,
            label=getattr(args, "label", None),
            source=getattr(args, "source", None),
            path=path,
        )
        print(f"Archived: {entry.expression}" + (f" ({entry.label})" if entry.label else ""))

    elif args.archive_cmd == "list":
        entries = list_archive(path=path)
        if not entries:
            print("Archive is empty.")
            return
        for e in entries:
            label_part = f"  [{e.label}]" if e.label else ""
            source_part = f"  via {e.source}" if e.source else ""
            print(f"{e.expression}{label_part}{source_part}  (archived {e.archived_at})")

    elif args.archive_cmd == "remove":
        removed = remove_from_archive(expression=args.expression, path=path)
        if removed:
            print(f"Removed '{args.expression}' from archive.")
        else:
            print(f"Expression '{args.expression}' not found in archive.", file=sys.stderr)
            sys.exit(1)

    elif args.archive_cmd == "clear":
        count = clear_archive(path=path)
        print(f"Cleared {count} archived expression(s).")
