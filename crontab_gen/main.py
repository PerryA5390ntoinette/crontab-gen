#!/usr/bin/env python3
"""crontab-gen: Interactive terminal utility for building, validating,
and documenting cron expressions with human-readable output."""

import sys
import argparse
from crontab_gen.builder import CronBuilder
from crontab_gen.validator import CronValidator
from crontab_gen.humanizer import CronHumanizer


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="crontab-gen",
        description="Build, validate, and document cron expressions interactively.",
    )
    subparsers = parser.add_subparsers(dest="command")

    # 'build' subcommand: interactive wizard
    subparsers.add_parser(
        "build",
        help="Interactively build a cron expression step by step.",
    )

    # 'validate' subcommand: validate an existing expression
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate an existing cron expression and show its meaning.",
    )
    validate_parser.add_argument(
        "expression",
        type=str,
        help='Cron expression to validate (e.g. "*/5 * * * *").',
    )

    # 'explain' subcommand: explain a cron expression in plain English
    explain_parser = subparsers.add_parser(
        "explain",
        help="Explain a cron expression in plain English.",
    )
    explain_parser.add_argument(
        "expression",
        type=str,
        help='Cron expression to explain (e.g. "0 9 * * 1-5").',
    )

    return parser.parse_args()


def cmd_build() -> None:
    """Run the interactive cron expression builder."""
    print("\n=== crontab-gen: Interactive Builder ===")
    builder = CronBuilder()
    expression = builder.run()
    if expression:
        humanizer = CronHumanizer()
        print(f"\nGenerated expression : {expression}")
        print(f"Human-readable       : {humanizer.humanize(expression)}")
        print("\nAdd to your crontab with:")
        print(f"  (crontab -l; echo '{expression} <your-command>') | crontab -")


def cmd_validate(expression: str) -> None:
    """Validate a cron expression and display the result."""
    validator = CronValidator()
    is_valid, errors = validator.validate(expression)
    if is_valid:
        humanizer = CronHumanizer()
        print(f"✔  Valid expression  : {expression}")
        print(f"   Human-readable    : {humanizer.humanize(expression)}")
    else:
        print(f"✘  Invalid expression: {expression}")
        for error in errors:
            print(f"   • {error}")
        sys.exit(1)


def cmd_explain(expression: str) -> None:
    """Explain a cron expression in plain English."""
    validator = CronValidator()
    is_valid, errors = validator.validate(expression)
    if not is_valid:
        print(f"✘  Cannot explain invalid expression: {expression}")
        for error in errors:
            print(f"   • {error}")
        sys.exit(1)

    humanizer = CronHumanizer()
    print(f"Expression   : {expression}")
    print(f"Explanation  : {humanizer.humanize(expression)}")


def main() -> None:
    """Main entry point for crontab-gen."""
    args = parse_args()

    if args.command == "build":
        cmd_build()
    elif args.command == "validate":
        cmd_validate(args.expression)
    elif args.command == "explain":
        cmd_explain(args.expression)
    else:
        # Default: launch interactive builder
        cmd_build()


if __name__ == "__main__":
    main()
