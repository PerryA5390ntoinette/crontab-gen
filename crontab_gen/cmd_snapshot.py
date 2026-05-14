"""CLI subcommand for managing cron expression snapshots."""
from __future__ import annotations

import argparse
import sys

from crontab_gen.expression import is_valid
from crontab_gen.explainer import explain
from crontab_gen.snapshot import add_snapshot, list_snapshots, clear_snapshots, DEFAULT_PATH
from crontab_gen.diff import diff


def add_snapshot_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("snapshot", help="Save and compare cron expression snapshots")
    sub = p.add_subparsers(dest="snapshot_cmd", required=True)

    save_p = sub.add_parser("save", help="Save a snapshot of a cron expression")
    save_p.add_argument("expression", help="Cron expression to snapshot")
    save_p.add_argument("--label", default=None, help="Optional label for this snapshot")
    save_p.add_argument("--file", default=DEFAULT_PATH, help="Snapshot storage file")

    list_p = sub.add_parser("list", help="List saved snapshots")
    list_p.add_argument("--file", default=DEFAULT_PATH, help="Snapshot storage file")

    clear_p = sub.add_parser("clear", help="Clear all snapshots")
    clear_p.add_argument("--file", default=DEFAULT_PATH, help="Snapshot storage file")

    compare_p = sub.add_parser("compare", help="Compare two saved snapshots by index")
    compare_p.add_argument("index_a", type=int, help="Index of first snapshot (0-based)")
    compare_p.add_argument("index_b", type=int, help="Index of second snapshot (0-based)")
    compare_p.add_argument("--file", default=DEFAULT_PATH, help="Snapshot storage file")

    p.set_defaults(func=cmd_snapshot)


def cmd_snapshot(args: argparse.Namespace) -> None:
    if args.snapshot_cmd == "save":
        if not is_valid(args.expression):
            print(f"Error: invalid cron expression '{args.expression}'", file=sys.stderr)
            sys.exit(1)
        entry = add_snapshot(args.expression, label=args.label, path=args.file)
        label_part = f" ({entry.label})" if entry.label else ""
        print(f"Snapshot saved: {entry.expression}{label_part}")
        print(f"  {explain(entry.expression)}")

    elif args.snapshot_cmd == "list":
        entries = list_snapshots(path=args.file)
        if not entries:
            print("No snapshots saved.")
            return
        for i, e in enumerate(entries):
            label_part = f" [{e.label}]" if e.label else ""
            print(f"  [{i}] {e.expression}{label_part}  ({e.created_at})")

    elif args.snapshot_cmd == "clear":
        count = clear_snapshots(path=args.file)
        print(f"Cleared {count} snapshot(s).")

    elif args.snapshot_cmd == "compare":
        entries = list_snapshots(path=args.file)
        for idx in (args.index_a, args.index_b):
            if idx < 0 or idx >= len(entries):
                print(f"Error: index {idx} out of range (have {len(entries)} snapshots)", file=sys.stderr)
                sys.exit(1)
        a = entries[args.index_a]
        b = entries[args.index_b]
        print(f"Comparing [{args.index_a}] {a.expression}  vs  [{args.index_b}] {b.expression}")
        result = diff(a.expression, b.expression)
        for fd in result.fields:
            marker = "*" if fd.changed else " "
            print(f"  {marker} {fd.field_name:<8}  {fd.before}  ->  {fd.after}")
