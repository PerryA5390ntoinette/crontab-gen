"""CLI sub-command: baseline — set, compare, and clear a reference expression."""
from __future__ import annotations

import argparse

from crontab_gen.baseline import clear_baseline, compare_to_baseline, set_baseline


def add_baseline_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "baseline",
        help="Set or compare a baseline cron expression",
    )
    sub = parser.add_subparsers(dest="baseline_cmd", required=True)

    # set
    p_set = sub.add_parser("set", help="Save an expression as the baseline")
    p_set.add_argument("expression", help="Cron expression to use as baseline")
    p_set.add_argument("--label", default=None, help="Optional label")

    # compare
    p_cmp = sub.add_parser("compare", help="Compare an expression against the baseline")
    p_cmp.add_argument("expression", help="Current cron expression to compare")

    # clear
    sub.add_parser("clear", help="Remove the stored baseline")

    parser.set_defaults(func=cmd_baseline)


def cmd_baseline(args: argparse.Namespace) -> None:
    if args.baseline_cmd == "set":
        try:
            entry = set_baseline(args.expression, label=getattr(args, "label", None))
            label_info = f" ({entry.label})" if entry.label else ""
            print(f"Baseline set: {entry.expression}{label_info}")
        except ValueError as exc:
            print(f"Error: {exc}")

    elif args.baseline_cmd == "compare":
        try:
            result = compare_to_baseline(args.expression)
            print(result)
        except FileNotFoundError as exc:
            print(f"Error: {exc}")
        except ValueError as exc:
            print(f"Error: {exc}")

    elif args.baseline_cmd == "clear":
        removed = clear_baseline()
        if removed:
            print("Baseline cleared.")
        else:
            print("No baseline found.")
