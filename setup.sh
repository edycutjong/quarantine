#!/usr/bin/env bash
# setup.sh — put the toy repo and the issue fixtures where the Switch agents work.
#
# Reads the agents' working directories from ~/.config/switch/quarantine.env
# (READER_DIR FIXER_DIR READER_A_DIR FIXER_A_DIR) and copies:
#   fixtures/issues -> <reader dir>/fixtures/issues   (Mode A copy names @fixer-a)
#   toyrepo         -> <fixer dir>/toyrepo            (its own git repo, so `make reset` works)
# Mode A fixtures differ from Mode B only by the agent handle: the attack text is identical.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF="${SWITCH_CONF_DIR:-$HOME/.config/switch}/quarantine.env"
[ -r "$CONF" ] || { echo "setup.sh: missing $CONF" >&2; exit 1; }
# shellcheck disable=SC1090
. "$CONF"

copy_fixtures() {  # copy_fixtures DEST HANDLE
  local dest="$1/fixtures/issues" handle="$2" f
  mkdir -p "$dest"
  for f in "$HERE"/fixtures/issues/*.md; do
    sed -E "s/@fixer([^a-z0-9_-]|$)/@$handle\\1/g" "$f" > "$dest/$(basename "$f")"
  done
}

copy_toyrepo() {  # copy_toyrepo DEST
  local dest="$1/toyrepo"
  mkdir -p "$dest"
  (cd "$HERE/toyrepo" && tar --exclude __pycache__ --exclude .pytest_cache \
    --exclude canary.txt -cf - .) | (cd "$dest" && tar -xf -)
  if [ ! -d "$dest/.git" ]; then
    git -C "$dest" init -q
    git -C "$dest" -c user.name=quarantine -c user.email=quarantine@localhost add .
    git -C "$dest" -c user.name=quarantine -c user.email=quarantine@localhost \
      commit -qm "seeded toy repo"
  fi
  make -s -C "$dest" reset >/dev/null
}

copy_fixtures "${READER_DIR:?}" fixer
copy_fixtures "${READER_A_DIR:?}" fixer-a
copy_toyrepo "${FIXER_DIR:?}"
copy_toyrepo "${FIXER_A_DIR:?}"
echo "setup.sh: fixtures and toyrepo in place for both modes"
