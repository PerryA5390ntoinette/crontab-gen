"""CLI subcommand: search — filter saved expressions by keyword or tag."""
from __future__ import annotations

import argparse
import sys

from crontab_gen.search import search


def add_search_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser(
        "search",
        help="Search saved tagged expressions by keyword or tag",
    )
    parser.add_argument(
        "keyword",
        nargs="?",
        default="",
        help="Keyword to match against expression, label, or description",
    )
    parser.add_argument(
        "--tag",
        default=None,
        metavar="TAG",
        help="Filter results to entries with this tag",
    )
    parser.add_argument(
        "--tags-file",
        default=None,
        metavar="PATH",
        help="Path to tags storage file (default: ~/.crontab_gen_tags.json)",
    )
    parser.set_defaults(func=cmd_search)


def cmd_search(args: argparse.Namespace) -> int:
    results = search(
        keyword=args.keyword,
        tag=args.tag,
        tags_file=getattr(args, "tags_file", None),
    )
    if not results:
        msg = "No matching expressions found."
        if args.keyword:
            msg = f"No results for '{args.keyword}'."
        print(msg)
        return 0

    print(f"Found {len(results)} result(s):\n")
    for r in results:
        label_part = f"  label : {r.label}" if r.label else ""
        tags_part = f"  tags  : {', '.join(r.matched_tags)}" if r.matched_tags else ""
        print(f"  expr  : {r.expression}")
        if label_part:
            print(label_part)
        print(f"  desc  : {r.description}")
        if tags_part:
            print(tags_part)
        print()
    return 0
