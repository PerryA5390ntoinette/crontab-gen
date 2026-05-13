"""CLI command handler for the 'presets' subcommand."""

import argparse
import sys

from .presets import get_preset, list_presets, categories
from .formatter import format_preset_table, format_preset_detail, format_categories
from .explainer import explain


def add_presets_subparser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'presets' subcommand."""
    parser = subparsers.add_parser(
        "presets",
        help="Browse and use common cron expression presets",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--list",
        metavar="CATEGORY",
        nargs="?",
        const="__all__",
        help="List presets, optionally filtered by category",
    )
    group.add_argument(
        "--show",
        metavar="NAME",
        help="Show details for a specific preset by name or alias",
    )
    group.add_argument(
        "--categories",
        action="store_true",
        help="List all available preset categories",
    )
    parser.set_defaults(func=cmd_presets)


def cmd_presets(args: argparse.Namespace) -> int:
    """Handle the 'presets' subcommand."""
    if args.categories:
        print(format_categories())
        return 0

    if args.show:
        preset = get_preset(args.show)
        if preset is None:
            print(f"Error: preset '{args.show}' not found.", file=sys.stderr)
            print(format_categories())
            return 1
        print(format_preset_detail(preset))
        print()
        print("Human-readable explanation:")
        print(" ", explain(preset.expression))
        return 0

    # Default: list
    category = None
    if args.list and args.list != "__all__":
        category = args.list
        known = categories()
        if category not in known:
            print(f"Error: unknown category '{category}'.", file=sys.stderr)
            print(format_categories())
            return 1

    print(format_preset_table(category))
    return 0
