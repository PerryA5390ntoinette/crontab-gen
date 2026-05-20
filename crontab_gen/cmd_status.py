"""CLI sub-command: status — show counts of all persisted artefacts."""
from __future__ import annotations

import argparse

from crontab_gen.status import build_status


def add_status_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the *status* sub-command on *subparsers*."""
    parser = subparsers.add_parser(
        "status",
        help="Show a summary of all stored cron artefacts.",
    )
    parser.add_argument(
        "--bookmarks",
        metavar="FILE",
        default=None,
        help="Path to bookmarks file (default: built-in default).",
    )
    parser.add_argument(
        "--favorites",
        metavar="FILE",
        default=None,
        help="Path to favorites file.",
    )
    parser.add_argument(
        "--history",
        metavar="FILE",
        default=None,
        help="Path to history file.",
    )
    parser.add_argument(
        "--notes",
        metavar="FILE",
        default=None,
        help="Path to notes file.",
    )
    parser.add_argument(
        "--snapshots",
        metavar="FILE",
        default=None,
        help="Path to snapshots file.",
    )
    parser.add_argument(
        "--tags",
        metavar="FILE",
        default=None,
        help="Path to tags file.",
    )
    parser.add_argument(
        "--templates",
        metavar="FILE",
        default=None,
        help="Path to templates file.",
    )
    parser.set_defaults(func=cmd_status)


def cmd_status(args: argparse.Namespace) -> None:
    """Execute the *status* sub-command."""
    report = build_status(
        bookmarks_path=args.bookmarks,
        favorites_path=args.favorites,
        history_path=args.history,
        notes_path=args.notes,
        snapshots_path=args.snapshots,
        tags_path=args.tags,
        templates_path=args.templates,
    )
    print(report)
