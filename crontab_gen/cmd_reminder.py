"""CLI sub-command: reminder — attach notes/reminders to cron expressions."""
from __future__ import annotations

import argparse
from pathlib import Path

from crontab_gen.reminder import DEFAULT_PATH, add_reminder, clear_reminders, list_reminders


def add_reminder_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("reminder", help="Manage reminders for cron expressions")
    sub = p.add_subparsers(dest="reminder_cmd", required=True)

    # add
    add_p = sub.add_parser("add", help="Attach a reminder message to an expression")
    add_p.add_argument("expression", help="Cron expression")
    add_p.add_argument("message", help="Reminder message")
    add_p.add_argument("--label", default=None, help="Optional label")
    add_p.add_argument("--file", type=Path, default=DEFAULT_PATH)

    # list
    list_p = sub.add_parser("list", help="List all reminders")
    list_p.add_argument("--file", type=Path, default=DEFAULT_PATH)

    # clear
    clear_p = sub.add_parser("clear", help="Remove all reminders")
    clear_p.add_argument("--file", type=Path, default=DEFAULT_PATH)

    p.set_defaults(func=cmd_reminder)


def cmd_reminder(args: argparse.Namespace) -> None:
    if args.reminder_cmd == "add":
        entry = add_reminder(
            expression=args.expression,
            message=args.message,
            label=getattr(args, "label", None),
            path=args.file,
        )
        label_part = f" [{entry.label}]" if entry.label else ""
        print(f"Reminder added{label_part}: {entry.expression!r} — {entry.message}")

    elif args.reminder_cmd == "list":
        entries = list_reminders(path=args.file)
        if not entries:
            print("No reminders saved.")
            return
        for e in entries:
            label_part = f" [{e.label}]" if e.label else ""
            print(f"{e.expression}{label_part}: {e.message}  (added {e.created_at})")

    elif args.reminder_cmd == "clear":
        count = clear_reminders(path=args.file)
        print(f"Cleared {count} reminder(s).")
