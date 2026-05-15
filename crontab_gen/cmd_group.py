"""CLI subcommand: group — manage named collections of cron expressions."""
from __future__ import annotations

import argparse
import sys

from crontab_gen.expression import is_valid
from crontab_gen.explainer import explain
from crontab_gen.group import add_group, get_group, list_groups, remove_group


def add_group_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("group", help="manage named groups of cron expressions")
    sub = p.add_subparsers(dest="group_cmd", required=True)

    # add
    p_add = sub.add_parser("add", help="create a new group")
    p_add.add_argument("name", help="group name")
    p_add.add_argument("expressions", nargs="+", help="cron expressions to include")
    p_add.add_argument("--description", "-d", default=None, help="optional description")

    # remove
    p_rm = sub.add_parser("remove", help="delete a group by name")
    p_rm.add_argument("name", help="group name")

    # list
    sub.add_parser("list", help="list all groups")

    # show
    p_show = sub.add_parser("show", help="show expressions in a group")
    p_show.add_argument("name", help="group name")

    p.set_defaults(func=cmd_group)


def cmd_group(args: argparse.Namespace) -> None:
    if args.group_cmd == "add":
        invalid = [e for e in args.expressions if not is_valid(e)]
        if invalid:
            print(f"Error: invalid expression(s): {', '.join(invalid)}", file=sys.stderr)
            sys.exit(1)
        entry = add_group(args.name, args.expressions, description=args.description)
        print(f"Group '{entry.name}' created with {len(entry.expressions)} expression(s).")

    elif args.group_cmd == "remove":
        removed = remove_group(args.name)
        if removed:
            print(f"Group '{args.name}' removed.")
        else:
            print(f"No group named '{args.name}' found.", file=sys.stderr)
            sys.exit(1)

    elif args.group_cmd == "list":
        groups = list_groups()
        if not groups:
            print("No groups saved.")
            return
        for g in groups:
            desc = f" — {g.description}" if g.description else ""
            print(f"{g.name} ({len(g.expressions)} expression(s)){desc}")

    elif args.group_cmd == "show":
        entry = get_group(args.name)
        if entry is None:
            print(f"No group named '{args.name}' found.", file=sys.stderr)
            sys.exit(1)
        if entry.description:
            print(f"Group: {entry.name} — {entry.description}")
        else:
            print(f"Group: {entry.name}")
        for expr in entry.expressions:
            print(f"  {expr:30s}  {explain(expr)}")
