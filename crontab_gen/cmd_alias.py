"""CLI subcommand for managing user-defined cron expression aliases."""
from __future__ import annotations

import argparse
import sys

from crontab_gen.alias import add_alias, get_alias, list_aliases, remove_alias, DEFAULT_PATH
from crontab_gen.expression import is_valid
from crontab_gen.explainer import explain


def add_alias_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("alias", help="Manage personal cron expression aliases")
    sub = parser.add_subparsers(dest="alias_cmd", required=True)

    # alias add <name> <expression> [--description TEXT]
    p_add = sub.add_parser("add", help="Add or update an alias")
    p_add.add_argument("name", help="Short alias name")
    p_add.add_argument("expression", help="Cron expression (quote it)")
    p_add.add_argument("-d", "--description", default="", help="Optional description")
    p_add.add_argument("--file", default=DEFAULT_PATH, help="Alias storage file")

    # alias remove <name>
    p_rm = sub.add_parser("remove", help="Remove an alias by name")
    p_rm.add_argument("name", help="Alias name to remove")
    p_rm.add_argument("--file", default=DEFAULT_PATH, help="Alias storage file")

    # alias show <name>
    p_show = sub.add_parser("show", help="Show details for a single alias")
    p_show.add_argument("name", help="Alias name")
    p_show.add_argument("--file", default=DEFAULT_PATH, help="Alias storage file")

    # alias list
    p_list = sub.add_parser("list", help="List all aliases")
    p_list.add_argument("--file", default=DEFAULT_PATH, help="Alias storage file")

    parser.set_defaults(func=cmd_alias)


def cmd_alias(args: argparse.Namespace) -> None:
    if args.alias_cmd == "add":
        if not is_valid(args.expression):
            print(f"Error: '{args.expression}' is not a valid cron expression.", file=sys.stderr)
            sys.exit(1)
        entry = add_alias(args.name, args.expression, args.description, path=args.file)
        print(f"Alias '{entry.name}' saved → {entry.expression}")

    elif args.alias_cmd == "remove":
        removed = remove_alias(args.name, path=args.file)
        if removed:
            print(f"Alias '{args.name}' removed.")
        else:
            print(f"No alias named '{args.name}' found.", file=sys.stderr)
            sys.exit(1)

    elif args.alias_cmd == "show":
        entry = get_alias(args.name, path=args.file)
        if entry is None:
            print(f"No alias named '{args.name}' found.", file=sys.stderr)
            sys.exit(1)
        print(f"Name       : {entry.name}")
        print(f"Expression : {entry.expression}")
        print(f"Description: {entry.description or '(none)'}")
        print(f"Explanation: {explain(entry.expression)}")

    elif args.alias_cmd == "list":
        entries = list_aliases(path=args.file)
        if not entries:
            print("No aliases defined.")
            return
        col = max(len(e.name) for e in entries)
        for e in entries:
            desc = f"  # {e.description}" if e.description else ""
            print(f"{e.name:<{col}}  {e.expression}{desc}")
