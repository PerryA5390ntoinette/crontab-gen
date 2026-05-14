import argparse
from .lint import lint
from .expression import CronExpression
from .history import add_entry


def add_lint_subparser(subparsers: argparse._SubParsersAction) -> None:
    """Register the 'lint' subcommand."""
    parser = subparsers.add_parser(
        "lint",
        help="Analyse a cron expression and report potential issues",
    )
    parser.add_argument(
        "expression",
        help="Cron expression to lint (5 fields, quoted)",
    )
    parser.add_argument(
        "--no-history",
        action="store_true",
        default=False,
        help="Do not record this expression in history",
    )
    parser.set_defaults(func=cmd_lint)


def cmd_lint(args: argparse.Namespace) -> int:
    """Execute the lint subcommand.

    Returns 0 when no warnings are found, 1 otherwise.
    """
    expr = CronExpression(args.expression)
    if not expr.is_valid():
        print(f"Error: '{args.expression}' is not a valid cron expression.")
        return 2

    result = lint(args.expression)

    if not args.no_history:
        add_entry(args.expression, command="lint")

    print(str(result))

    if result.ok:
        return 0
    return 1
