"""CLI subcommand: diff — compare two cron expressions."""

import argparse
import sys

from .diff import diff_expressions


def add_diff_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "diff",
        help="Compare two cron expressions field by field",
    )
    p.add_argument("left", help="First cron expression (quoted)")
    p.add_argument("right", help="Second cron expression (quoted)")
    p.add_argument(
        "--changed-only",
        action="store_true",
        default=False,
        help="Show only fields that differ",
    )
    p.set_defaults(func=cmd_diff)


def cmd_diff(args: argparse.Namespace) -> int:
    try:
        result = diff_expressions(args.left, args.right)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not result.has_changes:
        print("Expressions are identical.")
        return 0

    fields_to_show = result.changed_fields if args.changed_only else result.field_diffs
    header = f"{'FIELD':<10}  {'LEFT':<20}  {'RIGHT':<20}"
    print(header)
    print("-" * len(header))

    for fd in fields_to_show:
        marker = "*" if fd.changed else " "
        print(f"{marker} {fd.field.name:<9}  {fd.left:<20}  {fd.right:<20}")
        if fd.changed:
            print(f"  {'':10}  left : {fd.left_explanation}")
            print(f"  {'':10}  right: {fd.right_explanation}")

    return 0
