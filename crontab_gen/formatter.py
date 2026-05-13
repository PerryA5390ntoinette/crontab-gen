"""Format cron expressions and presets for terminal output."""

from typing import Optional

from .presets import CronPreset, list_presets, categories


COLUMN_WIDTHS = {
    "name": 22,
    "expression": 16,
    "alias": 12,
    "description": 50,
}


def _pad(text: str, width: int) -> str:
    return text.ljust(width)[:width]


def format_preset_row(preset: CronPreset) -> str:
    """Format a single preset as a table row."""
    alias = preset.alias or ""
    return (
        _pad(preset.name, COLUMN_WIDTHS["name"])
        + _pad(preset.expression, COLUMN_WIDTHS["expression"])
        + _pad(alias, COLUMN_WIDTHS["alias"])
        + preset.description
    )


def format_preset_table(category: Optional[str] = None) -> str:
    """Format all presets (or those in a category) as a table string."""
    presets = list_presets(category)
    if not presets:
        return f"No presets found for category: {category}"

    header = (
        _pad("NAME", COLUMN_WIDTHS["name"])
        + _pad("EXPRESSION", COLUMN_WIDTHS["expression"])
        + _pad("ALIAS", COLUMN_WIDTHS["alias"])
        + "DESCRIPTION"
    )
    separator = "-" * (sum(COLUMN_WIDTHS.values()) + 10)

    lines = [header, separator]
    current_cat = None
    for preset in presets:
        if category is None and preset.category != current_cat:
            current_cat = preset.category
            lines.append(f"\n[{current_cat.upper()}]")
        lines.append(format_preset_row(preset))

    return "\n".join(lines)


def format_preset_detail(preset: CronPreset) -> str:
    """Format detailed info for a single preset."""
    lines = [
        f"Name        : {preset.name}",
        f"Expression  : {preset.expression}",
        f"Description : {preset.description}",
        f"Category    : {preset.category}",
    ]
    if preset.alias:
        lines.append(f"Alias       : {preset.alias}")
    return "\n".join(lines)


def format_categories() -> str:
    """Format available categories as a comma-separated list."""
    return "Available categories: " + ", ".join(categories())
