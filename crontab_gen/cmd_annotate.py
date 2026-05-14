"""CLI subcommand: annotate — attach or view notes on cron expressions."""
from __future__ import annotations

import argparse
from pathlib import Path

from crontab_gen.annotate import (
    add_annotation,
    get_annotation,
    list_annotations,
    remove_annotation,
)
from crontab_gen.expression import is_valid

_DEFAULT_PATH = Path.home() / ".crontab_gen" / "annotations.json"


def add_annotate_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("annotate", help="Attach notes to cron expressions")
    sub = p.add_subparsers(dest="annotate_cmd", required=True)

    # set
    s = sub.add_parser("set", help="Add or update a note for an expression")
    s.add_argument("expression", help="Cron expression to annotate")
    s.add_argument("note", help="Freeform note text")
    s.add_argument("--file", type=Path, default=_DEFAULT_PATH)

    # get
    g = sub.add_parser("get", help="Retrieve the note for an expression")
    g.add_argument("expression", help="Cron expression to look up")
    g.add_argument("--file", type=Path, default=_DEFAULT_PATH)

    # remove
    r = sub.add_parser("remove", help="Delete the note for an expression")
    r.add_argument("expression", help="Cron expression whose note to remove")
    r.add_argument("--file", type=Path, default=_DEFAULT_PATH)

    # list
    l = sub.add_parser("list", help="List all annotated expressions")
    l.add_argument("--file", type=Path, default=_DEFAULT_PATH)

    p.set_defaults(func=cmd_annotate)


def cmd_annotate(args: argparse.Namespace) -> None:
    if args.annotate_cmd == "set":
        if not is_valid(args.expression):
            print(f"Error: '{args.expression}' is not a valid cron expression.")
            return
        entry = add_annotation(args.expression, args.note, path=args.file)
        action = "Updated" if entry.updated_at else "Added"
        print(f"{action} note for '{args.expression}'.")

    elif args.annotate_cmd == "get":
        entry = get_annotation(args.expression, path=args.file)
        if entry is None:
            print(f"No annotation found for '{args.expression}'.")
        else:
            print(f"Expression : {entry.expression}")
            print(f"Note       : {entry.note}")
            print(f"Created    : {entry.created_at}")
            if entry.updated_at:
                print(f"Updated    : {entry.updated_at}")

    elif args.annotate_cmd == "remove":
        removed = remove_annotation(args.expression, path=args.file)
        if removed:
            print(f"Removed annotation for '{args.expression}'.")
        else:
            print(f"No annotation found for '{args.expression}'.")

    elif args.annotate_cmd == "list":
        entries = list_annotations(path=args.file)
        if not entries:
            print("No annotations stored.")
            return
        for e in entries:
            updated = f"  [updated {e.updated_at}]" if e.updated_at else ""
            print(f"{e.expression:<20} {e.note}{updated}")
