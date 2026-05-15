"""CLI sub-command: pin — manage pinned cron expressions."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from crontab_gen.expression import is_valid
from crontab_gen.explainer import explain
from crontab_gen import pin as pin_mod


def add_pin_subparser(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("pin", help="Manage pinned cron expressions")
    sub = p.add_subparsers(dest="pin_cmd", required=True)

    # add
    add_p = sub.add_parser("add", help="Pin a cron expression")
    add_p.add_argument("expression", help="Cron expression to pin")
    add_p.add_argument("--label", default=None, help="Optional label")
    add_p.add_argument("--file", default=None, help="Custom pins file path")

    # remove
    rm_p = sub.add_parser("remove", help="Remove a pinned expression")
    rm_p.add_argument("expression", help="Cron expression to unpin")
    rm_p.add_argument("--file", default=None, help="Custom pins file path")

    # list
    ls_p = sub.add_parser("list", help="List all pinned expressions")
    ls_p.add_argument("--file", default=None, help="Custom pins file path")

    # clear
    cl_p = sub.add_parser("clear", help="Remove all pinned expressions")
    cl_p.add_argument("--file", default=None, help="Custom pins file path")

    p.set_defaults(func=cmd_pin)


def _resolve_path(args: argparse.Namespace) -> Path:
    if getattr(args, "file", None):
        return Path(args.file)
    return pin_mod._DEFAULT_PATH


def cmd_pin(args: argparse.Namespace) -> None:
    path = _resolve_path(args)

    if args.pin_cmd == "add":
        if not is_valid(args.expression):
            print(f"Error: '{args.expression}' is not a valid cron expression.", file=sys.stderr)
            sys.exit(1)
        entry = pin_mod.add_pin(args.expression, label=getattr(args, "label", None), path=path)
        label_part = f" ({entry.label})" if entry.label else ""
        print(f"Pinned: {entry.expression}{label_part}")

    elif args.pin_cmd == "remove":
        removed = pin_mod.remove_pin(args.expression, path=path)
        if removed:
            print(f"Unpinned: {args.expression}")
        else:
            print(f"Not found: {args.expression}", file=sys.stderr)
            sys.exit(1)

    elif args.pin_cmd == "list":
        entries = pin_mod.list_pins(path=path)
        if not entries:
            print("No pinned expressions.")
            return
        for e in entries:
            label_part = f"  # {e.label}" if e.label else ""
            description = explain(e.expression)
            print(f"{e.expression:<30}{label_part}")
            print(f"  → {description}")

    elif args.pin_cmd == "clear":
        count = pin_mod.clear_pins(path=path)
        print(f"Cleared {count} pinned expression(s).")
