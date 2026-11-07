"""setup.sh --offline: fixtures land in both readers' dirs (Mode A renamed), toy repos are seeded git repos."""
import shutil
import subprocess

import pytest

from conftest import ROOT

pytestmark = pytest.mark.skipif(shutil.which("make") is None or shutil.which("git") is None,
                                reason="needs make and git")


def run_setup(conf, dirs):
    conf.mkdir()
    (conf / "quarantine.env").write_text(
        "".join(f"{k}={v}\n" for k, v in dirs.items()))
    return subprocess.run(["bash", str(ROOT / "setup.sh"), "--offline"],
                          env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
                               "HOME": str(conf.parent), "SWITCH_CONF_DIR": str(conf)},
                          capture_output=True, text=True)


def test_offline_copy_is_idempotent_and_renames_only_the_handle(tmp_path):
    dirs = {k: tmp_path / k.lower() for k in ("READER_DIR", "FIXER_DIR", "READER_A_DIR", "FIXER_A_DIR")}
    res = run_setup(tmp_path / "conf", dirs)
    assert res.returncode == 0, res.stderr

    src = (ROOT / "fixtures/issues/04.md").read_text()
    mode_b = (dirs["READER_DIR"] / "fixtures/issues/04.md").read_text()
    mode_a = (dirs["READER_A_DIR"] / "fixtures/issues/04.md").read_text()
    assert mode_b == src
    assert "@fixer-a" in mode_a and mode_a.replace("@fixer-a", "@fixer") == src

    for key in ("FIXER_DIR", "FIXER_A_DIR"):
        repo = dirs[key] / "toyrepo"
        assert (repo / ".git").is_dir() and (repo / "invoice/discount.py").is_file()
        # a fixer edit plus a canary are wiped by the next setup run
        (repo / "invoice/discount.py").write_text("# edited by an agent\n")
        (repo / "canary.txt").write_text("x\n")

    res = subprocess.run(["bash", str(ROOT / "setup.sh"), "--offline"],
                         env={"PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
                              "HOME": str(tmp_path), "SWITCH_CONF_DIR": str(tmp_path / "conf")},
                         capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    for key in ("FIXER_DIR", "FIXER_A_DIR"):
        repo = dirs[key] / "toyrepo"
        assert not (repo / "canary.txt").exists()
        assert (repo / "invoice/discount.py").read_text() == \
            (ROOT / "toyrepo/invoice/discount.py").read_text()
