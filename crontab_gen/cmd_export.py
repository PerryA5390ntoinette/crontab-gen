"""CLI sub-command: export cron expressions to JSON, shell, or markdown."""
from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from crontab_gen.expression import is_valid
from crontab_gen.export import export_json, export_shell, export_markdown

FORMATS = ("json", "shell", "markdown")


def add_export_subparser(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser(
        "export",
        help="Export one or more cron expressions to JSON, shell snippet, or Markdown.",
    )
    p.add_argument(
        "expressions",
        nargs="+",
        metavar="EXPR",
        help="Cron expression(s) to export.",
    )
    p.add_argument(
        "--format",
        choices=FORMATS,
        default="json",
        dest="fmt",
        help="Output format (default: json).",
    )
    p.add_argument(
        "--labels",
        nargs="+",
        metavar="LABEL",
        default=None,
        help="Optional labels aligned with each expression.",
    )
    p.set_defaults(func=cmd_export)


def cmd_export(args: argparse.Namespace) -> int:
    expressions: List[str] = args.expressions
    labels: Optional[List[str]] = args.labels
    fmt: str = args.fmt

    if labels and len(labels) != len(expressions):
        print(
            f"Error: number of labels ({len(labels)}) must match "
            f"number of expressions ({len(expressions)}).",
            file=sys.stderr,
        )
        return 1

    for expr in expressions:
        if not is_valid(expr):
            print(f"Error: invalid cron expression: {expr!r}", file=sys.stderr)
            return 1

    if fmt == "json":
        output = export_json(expressions, labels)
    elif fmt == "shell":
        output = export_shell(expressions, labels)
    else:
        output = export_markdown(expressions, labels)

    print(output)
    return 0
