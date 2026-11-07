.PHONY: help test lint shellcheck audit ci

help:
	@echo "make test        offline tests (pytest)"
	@echo "make lint        ruff"
	@echo "make shellcheck  shellcheck setup.sh + bench"
	@echo "make audit       gitleaks over full history"
	@echo "make ci          all of the above"

test:
	python3 -m pytest -q tests

lint:
	ruff check .

shellcheck:
	shellcheck setup.sh bench/*.sh

audit:
	gitleaks detect --source . --log-opts="--all" --redact --no-banner

ci: lint test shellcheck audit
