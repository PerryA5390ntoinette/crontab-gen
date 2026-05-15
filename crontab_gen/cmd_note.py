"""CLI subcommand for managing expression notes."""
from __future__ import annotations

import argparse
from pathlib import Path

from crontab_gen.note import add_note, list_notes, remove_note, update_note

_DEFAULT_PATH = Path.home() / ".crontab_gen" / "notes.json"


def add_note_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("note", help="Manage notes attached to cron expressions")
    sub = p.add_subparsers(dest="note_cmd", required=True)

    add_p = sub.add_parser("add", help="Add a note to an expression")
    add_p.add_argument("expression", help="Cron expression")
    add_p.add_argument("text", help="Note text")

    list_p = sub.add_parser("list", help="List notes")
    list_p.add_argument("expression", nargs="?", default=None, help="Filter by expression")

    rm_p = sub.add_parser("remove", help="Remove a note by index")
    rm_p.add_argument("expression", help="Cron expression")
    rm_p.add_argument("index", type=int, help="Zero-based note index")

    up_p = sub.add_parser("update", help="Update note text by index")
    up_p.add_argument("expression", help="Cron expression")
    up_p.add_argument("index", type=int, help="Zero-based note index")
    up_p.add_argument("text", help="New note text")

    p.set_defaults(func=cmd_note)


def cmd_note(args: argparse.Namespace) -> None:
    path = _DEFAULT_PATH

    if args.note_cmd == "add":
        entry = add_note(args.expression, args.text, path=path)
        print(f"Note added for '{entry.expression}': {entry.text}")

    elif args.note_cmd == "list":
        entries = list_notes(expression=args.expression, path=path)
        if not entries:
            print("No notes found.")
            return
        for i, e in enumerate(entries):
            updated = f" (updated: {e.updated_at})" if e.updated_at else ""
            print(f"[{i}] {e.expression} | {e.text} | created: {e.created_at}{updated}")

    elif args.note_cmd == "remove":
        removed = remove_note(args.expression, args.index, path=path)
        if removed:
            print(f"Note {args.index} removed for '{args.expression}'.")
        else:
            print(f"No note at index {args.index} for '{args.expression}'.")

    elif args.note_cmd == "update":
        entry = update_note(args.expression, args.index, args.text, path=path)
        if entry:
            print(f"Note {args.index} updated for '{entry.expression}': {entry.text}")
        else:
            print(f"No note at index {args.index} for '{args.expression}'.")
