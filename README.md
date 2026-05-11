# crontab-gen

> Interactive terminal utility for building, validating, and documenting cron expressions with human-readable output.

---

## Installation

```bash
pip install crontab-gen
```

Or install from source:

```bash
git clone https://github.com/youruser/crontab-gen.git && cd crontab-gen && pip install .
```

---

## Usage

Launch the interactive prompt:

```bash
crontab-gen
```

You can also validate or explain an existing expression directly:

```bash
crontab-gen "*/15 9-17 * * 1-5"
```

**Example output:**

```
Expression : */15 9-17 * * 1-5
Description: Every 15 minutes, between 09:00 and 17:59,
             Monday through Friday
Next runs  :
  → 2024-06-10 09:00
  → 2024-06-10 09:15
  → 2024-06-10 09:30
```

In interactive mode, `crontab-gen` walks you through each field (minute, hour, day, month, weekday) step by step, suggests common presets, and confirms the final expression before copying it to your clipboard.

---

## Features

- 🛠 Step-by-step interactive builder
- ✅ Expression validation with clear error messages
- 📖 Human-readable description of any cron expression
- 🕒 Preview of upcoming scheduled run times
- 📋 Clipboard copy on confirmation

---

## Requirements

- Python 3.8+

---

## License

This project is licensed under the [MIT License](LICENSE).