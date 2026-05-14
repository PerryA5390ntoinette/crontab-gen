"""CLI subcommand: suggest cron expressions from a keyword query."""

from __future__ import annotations

import argparse
from typing import List

from crontab_gen.suggest import suggest, Suggestion


def add_suggest_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    parser = subparsers.add_parser(
        "suggest",
        help="Suggest cron expressions based on a keyword query",
    )
    parser.add_argument(
        "query",
        nargs="?",
        default="",
        help="Keyword(s) to search for (e.g. 'daily', 'every 5 minutes')",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=5,
        metavar="N",
        help="Maximum number of suggestions to show (default: 5)",
    )
    parser.add_argument(
        "--no-header",
        action="store_true",
        default=False,
        help="Suppress the header line",
    )
    parser.set_defaults(func=cmd_suggest)


def _format_suggestions(suggestions: List[Suggestion], no_header: bool) -> str:
    if not suggestions:
        return "No suggestions found."

    col_w = max(len(s.expression) for s in suggestions) + 2
    lines = []
    if not no_header:
        lines.append(f"{'Expression':<{col_w}} Description")
        lines.append("-" * (col_w + 30))
    for s in suggestions:
        lines.append(f"{s.expression:<{col_w}} {s.description}")
    return "\n".join(lines)


def cmd_suggest(args: argparse.Namespace) -> int:
    results = suggest(args.query, limit=args.limit)
    print(_format_suggestions(results, no_header=args.no_header))
    return 0
