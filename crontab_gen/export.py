"""Export cron expressions to various formats (JSON, TOML, shell snippet)."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from typing import List, Optional

from crontab_gen.expression import CronExpression
from crontab_gen.explainer import explain


@dataclass
class ExportEntry:
    expression: str
    description: str
    label: Optional[str] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


def _build_entry(expr: str, label: Optional[str] = None) -> ExportEntry:
    description = explain(CronExpression(expr))
    return ExportEntry(expression=expr, description=description, label=label)


def export_json(expressions: List[str], labels: Optional[List[str]] = None) -> str:
    """Return a JSON string for a list of cron expressions."""
    labels = labels or [None] * len(expressions)
    entries = [_build_entry(e, l).to_dict() for e, l in zip(expressions, labels)]
    return json.dumps(entries, indent=2)


def export_shell(expressions: List[str], labels: Optional[List[str]] = None) -> str:
    """Return a crontab-style shell snippet with inline comments."""
    labels = labels or [None] * len(expressions)
    lines: List[str] = []
    for expr, label in zip(expressions, labels):
        description = explain(CronExpression(expr))
        comment = label if label else description
        lines.append(f"# {comment}")
        lines.append(f"{expr} /path/to/command")
        lines.append("")
    return "\n".join(lines).rstrip()


def export_markdown(expressions: List[str], labels: Optional[List[str]] = None) -> str:
    """Return a Markdown table of cron expressions."""
    labels = labels or [None] * len(expressions)
    header = "| Expression | Label | Description |"
    separator = "|---|---|---|"
    rows = [header, separator]
    for expr, label in zip(expressions, labels):
        description = explain(CronExpression(expr))
        lbl = label or ""
        rows.append(f"| `{expr}` | {lbl} | {description} |")
    return "\n".join(rows)
