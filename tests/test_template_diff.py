"""The two templates must differ only by the -a suffix and the fixer's addressing word.

That is the whole experiment: same agents, same instructions, same room; one word of
Switch policy decides whether a poisoned issue can drive the privileged agent.
"""

import difflib
import re

import yaml

SUFFIXED = re.compile(r"\b(reader|fixer|intake)-a\b")


def _code_lines(path):
    return [ln for ln in path.read_text().splitlines() if not ln.lstrip().startswith("#")]


def _normalised(path):
    return [SUFFIXED.sub(r"\1", ln) for ln in _code_lines(path)]


def test_templates_differ_by_one_word(root):
    secure = _normalised(root / "quarantine.template.yaml")
    unsafe = _normalised(root / "quarantine-unsafe.template.yaml")
    changed = [
        ln for ln in difflib.unified_diff(secure, unsafe, lineterm="", n=0)
        if ln[:1] in "+-" and not ln.startswith(("+++", "---"))
    ]
    assert changed == ["-    addressing: owner", "+    addressing: owner-agents"]


def test_addressing_per_mode(root):
    secure = yaml.safe_load((root / "quarantine.template.yaml").read_text())
    unsafe = yaml.safe_load((root / "quarantine-unsafe.template.yaml").read_text())
    assert {a["name"]: a["addressing"] for a in secure["agents"]} == {
        "reader": "owner", "fixer": "owner"}
    assert {a["name"]: a["addressing"] for a in unsafe["agents"]} == {
        "reader-a": "owner", "fixer-a": "owner-agents"}
    assert secure["room"]["name"] == "intake"
    assert unsafe["room"]["name"] == "intake-a"


AGENT_FIELDS = {
    "name", "display_name", "icon_url", "description", "instructions", "provider",
    "machine", "location", "directory", "model", "advanced_config", "isolation",
    "auto_mode", "auto_approve", "can_manage_agents", "connections", "repo", "sources",
    "addressing", "join", "allow_existing",
}
ROOM_FIELDS = {
    "name", "description", "instructions", "bridge", "channel_type", "read_visibility",
    "write_visibility", "agents", "users", "roles", "references", "packages", "docs",
    "aliases",
}
TOP_FIELDS = {"version", "params", "agent", "agents", "room", "group", "rooms", "links",
              "kickoff", "form"}


def test_only_documented_template_fields(root):
    """Field names come from Switch's TEMPLATES.md (agent block / room block)."""
    for name in ("quarantine.template.yaml", "quarantine-unsafe.template.yaml"):
        doc = yaml.safe_load((root / name).read_text())
        assert set(doc) <= TOP_FIELDS
        for agent in doc["agents"]:
            assert set(agent) <= AGENT_FIELDS, name
            # Switch requires provider, where it runs, and directory on every created agent.
            assert {"provider", "directory", "instructions"} <= set(agent)
            assert "location" in agent or "machine" in agent
        assert set(doc["room"]) <= ROOM_FIELDS, name


def test_switch_bug_workarounds(root):
    for name in ("quarantine.template.yaml", "quarantine-unsafe.template.yaml"):
        doc = yaml.safe_load((root / name).read_text())
        for agent in doc["agents"]:
            # switch#1577: no {placeholders} inside managed-agent instructions.
            assert "{" not in agent["instructions"] and "}" not in agent["instructions"]
            # switch#1580: long Mattermost replies are dropped, so replies are capped.
            assert "5 short lines" in agent["instructions"]
        # switch#1158: kickoff is one plain sentence that mentions only the reader.
        mentions = re.findall(r"@([a-z0-9._-]+)", doc["kickoff"])
        assert len(mentions) == 1 and mentions[0].startswith("reader")
        assert "\n" not in doc["kickoff"].strip()
