# Contributing

Thanks for your interest in improving QUARANTINE.

## Getting started
1. Fork the repo and branch from `main`: `git checkout -b feat/your-change`
2. Offline checks need only Python 3.11+: `pip install pytest pyyaml ruff`
3. The live path needs Switch Console with its local server running; see [README → Getting Started](../README.md#-getting-started).

## Before you open a PR
- `python -m pytest -q tests` passes (offline: templates, fixtures, seeded toy repo, bench parser, setup.sh).
- `ruff check .` and `shellcheck setup.sh bench/*.sh` are clean.
- The two templates must still differ only by the fixer's `addressing:` and the `-a` suffix (`tests/test_template_diff.py` enforces it).
- Never commit credentials. Mattermost/Switch settings live in `~/.config/switch/`, outside the repo.
- Files in `fixtures/issues/` contain prompt-injection text on purpose: keep them inert (the canary only writes a date).

## Reporting bugs / requesting features
Open an issue with the templates provided. Include the Switch Console version, the mode (A or B) and the room export if relevant.
