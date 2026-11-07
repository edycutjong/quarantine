"""Lint fixtures/issues: front matter shape, and which injections carry a live mention."""

import re

import pytest
import yaml

STYLES = {"direct", "maintainer-note", "code-block", "html-comment", "polite-relay",
          "authority", "split"}
BUGS = {"discount-rounding", "due-date-weekend", "tax-on-discounted"}
LIVE_FIXER = re.compile(r"@fixer\b")


def _load(path):
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    assert m, f"{path.name}: missing front matter"
    return yaml.safe_load(m.group(1)), m.group(2)


def _all(root):
    files = sorted((root / "fixtures" / "issues").glob("*.md"))
    return [(p, *_load(p)) for p in files]


def test_ten_fixtures_numbered(root):
    names = [p.name for p, _, _ in _all(root)]
    assert names == [f"{i:02d}.md" for i in range(1, 11)]


def test_front_matter(root):
    for path, meta, body in _all(root):
        assert meta["id"] == int(path.stem)
        assert meta["title"].strip()
        assert body.strip()
        if meta["kind"] == "genuine":
            assert meta["bug"] in BUGS and "style" not in meta
        else:
            assert meta["kind"] == "injection"
            assert meta["style"] in STYLES and "bug" not in meta


def test_mix_three_genuine_seven_injections(root):
    metas = [m for _, m, _ in _all(root)]
    assert sorted(m["bug"] for m in metas if m["kind"] == "genuine") == sorted(BUGS)
    assert sorted(m["style"] for m in metas if m["kind"] == "injection") == sorted(STYLES)


@pytest.mark.parametrize("fid", range(1, 11))
def test_live_mention(root, fid):
    """Every injection names @fixer except #10 (split across lines, the control)."""
    path = root / "fixtures" / "issues" / f"{fid:02d}.md"
    meta, body = _load(path)
    has_mention = bool(LIVE_FIXER.search(body))
    expected = meta["kind"] == "injection" and fid != 10
    assert has_mention is expected


def test_every_injection_targets_make_canary(root):
    for _, meta, body in _all(root):
        if meta["kind"] == "injection":
            # #10 splits the words across lines; joined, it still asks for make canary.
            assert "canary" in body.replace("\n", "")
