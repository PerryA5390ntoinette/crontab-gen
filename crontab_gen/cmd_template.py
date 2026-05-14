"""CLI subcommand for managing cron expression templates."""
from __future__ import annotations

import argparse
import sys

from crontab_gen.expression import is_valid
from crontab_gen.explainer import explain
from crontab_gen.template import (
    delete_template,
    get_template,
    list_templates,
    save_template,
)


def add_template_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("template", help="Manage saved cron templates")
    sub = parser.add_subparsers(dest="template_cmd", required=True)

    # save
    p_save = sub.add_parser("save", help="Save a named template")
    p_save.add_argument("name", help="Template name")
    p_save.add_argument("expression", help="Cron expression")
    p_save.add_argument("-d", "--description", default="", help="Optional description")
    p_save.add_argument("-t", "--tags", nargs="*", default=[], help="Optional tags")

    # get
    p_get = sub.add_parser("get", help="Retrieve a template by name")
    p_get.add_argument("name", help="Template name")

    # list
    sub.add_parser("list", help="List all saved templates")

    # delete
    p_del = sub.add_parser("delete", help="Delete a template by name")
    p_del.add_argument("name", help="Template name")


def cmd_template(args: argparse.Namespace) -> None:
    cmd = args.template_cmd

    if cmd == "save":
        if not is_valid(args.expression):
            print(f"Error: invalid cron expression: {args.expression}", file=sys.stderr)
            sys.exit(1)
        entry = save_template(
            name=args.name,
            expression=args.expression,
            description=args.description,
            tags=args.tags,
        )
        print(f"Template '{entry.name}' saved ({entry.expression})")

    elif cmd == "get":
        entry = get_template(args.name)
        if entry is None:
            print(f"Template '{args.name}' not found.", file=sys.stderr)
            sys.exit(1)
        print(f"Name       : {entry.name}")
        print(f"Expression : {entry.expression}")
        print(f"Description: {entry.description}")
        print(f"Tags       : {', '.join(entry.tags) if entry.tags else '-'}")
        print(f"Meaning    : {explain(entry.expression)}")

    elif cmd == "list":
        entries = list_templates()
        if not entries:
            print("No templates saved.")
            return
        for e in entries:
            tag_str = f"  [{', '.join(e.tags)}]" if e.tags else ""
            print(f"  {e.name:<20} {e.expression:<25} {e.description}{tag_str}")

    elif cmd == "delete":
        removed = delete_template(args.name)
        if removed:
            print(f"Template '{args.name}' deleted.")
        else:
            print(f"Template '{args.name}' not found.", file=sys.stderr)
            sys.exit(1)
