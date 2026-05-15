"""CLI subcommand for managing favorite cron expressions."""
from __future__ import annotations

import argparse
from pathlib import Path

from crontab_gen.favorite import (
    add_favorite,
    list_favorites,
    remove_favorite,
    clear_favorites,
    _DEFAULT_PATH,
)
from crontab_gen.explainer import explain


def add_favorite_subparser(subparsers: argparse.Action) -> None:
    p = subparsers.add_parser("favorite", help="Manage favorite cron expressions")
    p.add_argument("--file", type=Path, default=_DEFAULT_PATH, help="Favorites file path")
    sub = p.add_subparsers(dest="fav_cmd", required=True)

    add_p = sub.add_parser("add", help="Add a favorite")
    add_p.add_argument("expression", help="Cron expression")
    add_p.add_argument("--label", default=None, help="Human-readable label")
    add_p.add_argument("--tags", nargs="*", default=[], help="Optional tags")

    sub.add_parser("list", help="List all favorites")

    rm_p = sub.add_parser("remove", help="Remove a favorite by expression")
    rm_p.add_argument("expression", help="Cron expression to remove")

    sub.add_parser("clear", help="Remove all favorites")


def cmd_favorite(args: argparse.Namespace) -> None:
    path: Path = args.file

    if args.fav_cmd == "add":
        entry = add_favorite(args.expression, label=args.label, tags=args.tags, path=path)
        label_part = f" ({entry.label})" if entry.label else ""
        print(f"Saved favorite: {entry.expression}{label_part}")

    elif args.fav_cmd == "list":
        entries = list_favorites(path=path)
        if not entries:
            print("No favorites saved.")
            return
        for e in entries:
            label_part = f"  [{e.label}]" if e.label else ""
            tags_part = f"  tags={e.tags}" if e.tags else ""
            desc = explain(e.expression)
            print(f"{e.expression}{label_part}{tags_part}")
            print(f"  -> {desc}")

    elif args.fav_cmd == "remove":
        removed = remove_favorite(args.expression, path=path)
        if removed:
            print(f"Removed favorite: {args.expression}")
        else:
            print(f"No favorite found for: {args.expression}")

    elif args.fav_cmd == "clear":
        count = clear_favorites(path=path)
        print(f"Cleared {count} favorite(s).")
