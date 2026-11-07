#!/usr/bin/env python3
"""Pre-submit gate: files a judge needs exist, README links resolve in the repo, no measured cell left pending.

  python3 scripts/check_submission_readiness.py           # report; exit 1 on any FAIL
  python3 scripts/check_submission_readiness.py --allow-pending   # pending live results are WARN, not FAIL
Stdlib only.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = [
    "README.md", "DEMO.md", "ARCHITECTURE.md", "LICENSE", "SECURITY.md", "docs/FRICTION.md",
    "docs/architecture.svg", "docs/architecture.png", "docs/icon.svg",
    "quarantine.template.yaml", "quarantine-unsafe.template.yaml", "setup.sh", "bench/inject.sh",
]
FORBIDDEN = re.compile(r"(^|/)(CLAUDE\.md|AGENTS\.md|\.claude|specs|progress\.md|graphify-out)(/|$)|\.env$|\.pem$", re.I)
LINK = re.compile(r"\]\(([^)\s]+)\)|(?:src|href)=\"([^\"]+)\"")


def main(argv):
    allow_pending = "--allow-pending" in argv
    fails, warns = [], []
    for rel in REQUIRED:
        p = ROOT / rel
        if not p.is_file() or p.stat().st_size == 0:
            fails.append(f"missing or empty: {rel}")
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT).as_posix()
        if rel.startswith(".git/"):
            continue
        if FORBIDDEN.search(rel):
            fails.append(f"kitchen/secret path in repo: {rel}")
    for doc in ("README.md", "ARCHITECTURE.md", "DEMO.md"):
        p = ROOT / doc
        if not p.is_file():
            continue
        text = p.read_text(encoding="utf-8")
        for m in LINK.finditer(text):
            target = (m.group(1) or m.group(2)).split("#")[0]
            if not target or re.match(r"^(https?:|mailto:)", target):
                continue
            if not (ROOT / target).exists():
                fails.append(f"{doc}: broken repo link {target}")
        if re.search(r"\bpending\b", text, re.I):
            (warns if allow_pending else fails).append(f"{doc}: still has 'pending' cells")
    for w in warns:
        print("WARN", w)
    for f in fails:
        print("FAIL", f)
    print(f"{'NOT READY' if fails else 'READY'}: {len(fails)} fail, {len(warns)} warn")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
