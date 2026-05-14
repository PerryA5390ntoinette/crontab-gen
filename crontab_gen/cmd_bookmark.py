"""CLI subcommand for managing bookmarks."""
from __future__ import annotations

import argparse
import sys

from crontab_gen.bookmark import add_bookmark, find_bookmark, list_bookmarks, remove_bookmark
from crontab_gen.explainer import explain
from crontab_gen.expression import is_valid


def add_bookmark_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("bookmark", help="Manage bookmarked cron expressions")
    sub = parser.add_subparsers(dest="bookmark_cmd", required=True)

    p_add = sub.add_parser("add", help="Bookmark an expression")
    p_add.add_argument("expression", help="Cron expression to bookmark")
    p_add.add_argument("label", help="Short label for the bookmark")

    p_remove = sub.add_parser("remove", help="Remove a bookmark by label")
    p_remove.add_argument("label", help="Label of the bookmark to remove")

    sub.add_parser("list", help="List all bookmarks")

    p_show = sub.add_parser("show", help="Show details for a bookmark")
    p_show.add_argument("label", help="Label of the bookmark to show")

    parser.set_defaults(func=cmd_bookmark)


def cmd_bookmark(args: argparse.Namespace) -> None:
    bm_cmd = args.bookmark_cmd

    if bm_cmd == "add":
        if not is_valid(args.expression):
            print(f"Error: '{args.expression}' is not a valid cron expression.", file=sys.stderr)
            sys.exit(1)
        entry = add_bookmark(
            expression=args.expression,
            label=args.label,
            path=getattr(args, "bookmark_file", None) or _default_path(),
        )
        print(f"Bookmarked '{entry.expression}' as '{entry.label}'.")

    elif bm_cmd == "remove":
        removed = remove_bookmark(
            label=args.label,
            path=getattr(args, "bookmark_file", None) or _default_path(),
        )
        if removed:
            print(f"Removed bookmark '{args.label}'.")
        else:
            print(f"No bookmark found with label '{args.label}'.", file=sys.stderr)
            sys.exit(1)

    elif bm_cmd == "list":
        entries = list_bookmarks(path=getattr(args, "bookmark_file", None) or _default_path())
        if not entries:
            print("No bookmarks saved.")
        else:
            for e in entries:
                print(f"{e.label:<20}  {e.expression}")

    elif bm_cmd == "show":
        entry = find_bookmark(
            label=args.label,
            path=getattr(args, "bookmark_file", None) or _default_path(),
        )
        if entry is None:
            print(f"No bookmark found with label '{args.label}'.", file=sys.stderr)
            sys.exit(1)
        print(f"Label      : {entry.label}")
        print(f"Expression : {entry.expression}")
        print(f"Description: {explain(entry.expression)}")
        print(f"Created    : {entry.created_at}")


def _default_path() -> str:
    from crontab_gen.bookmark import DEFAULT_PATH
    return DEFAULT_PATH
