"""CLI subcommand: overlap — detect scheduling conflicts between cron expressions."""
from __future__ import annotations

import argparse
import sys

from .overlap import detect_overlap, overlap_matrix


def add_overlap_subparser(subparsers) -> None:
    parser = subparsers.add_parser(
        "overlap",
        help="Detect overlapping fire times between cron expressions.",
    )
    parser.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Two or more cron expressions to compare.",
    )
    parser.add_argument(
        "--lookahead",
        type=int,
        default=100,
        metavar="N",
        help="Number of upcoming runs to sample per expression (default: 100).",
    )
    parser.add_argument(
        "--matrix",
        action="store_true",
        default=False,
        help="Show overlap counts for all pairs instead of detailed output.",
    )
    parser.set_defaults(func=cmd_overlap)


def cmd_overlap(args: argparse.Namespace) -> None:
    expressions = args.expressions
    lookahead = args.lookahead

    if len(expressions) < 2:
        print("Error: at least two expressions are required.", file=sys.stderr)
        sys.exit(1)

    try:
        if args.matrix:
            pairs = overlap_matrix(expressions, lookahead=lookahead)
            if not pairs:
                print("No overlaps found among the provided expressions.")
            else:
                print(f"{'Expression A':<30} {'Expression B':<30} {'Shared'}")  
                print("-" * 70)
                for a, b, count in pairs:
                    print(f"{a:<30} {b:<30} {count}")
        else:
            if len(expressions) != 2:
                print(
                    "Error: provide exactly two expressions for detailed output, "
                    "or use --matrix for multiple.",
                    file=sys.stderr,
                )
                sys.exit(1)
            result = detect_overlap(expressions[0], expressions[1], lookahead=lookahead)
            print(result)
            if result.has_overlap:
                print("\nShared fire times:")
                for t in result.shared_times:
                    print(f"  {t}")
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
