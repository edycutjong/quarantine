#!/usr/bin/env bash
# setup.sh — check the Switch rooms are live, then put the toy repo and the issue
# fixtures where the agents work. Idempotent: safe to run before every demo or bench.
#
#   ./setup.sh            checks (Mattermost ping, both rooms, !list-agents in each) + copy
#   ./setup.sh --offline  copy only (no Mattermost needed)
#
# Reads ~/.config/switch/mattermost.env (MM_URL MM_TEAM) and ~/.config/switch/quarantine.env
# (MM_USER_TOKEN, READER_DIR FIXER_DIR READER_A_DIR FIXER_A_DIR = the agents' working dirs) and copies:
#   fixtures/issues -> <reader dir>/fixtures/issues   (Mode A copy names @fixer-a)
#   toyrepo         -> <fixer dir>/toyrepo            (its own git repo, so `make reset` works)
# Mode A fixtures differ from Mode B only by the agent handle: the attack text is identical.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONF_DIR="${SWITCH_CONF_DIR:-$HOME/.config/switch}"
LIST_WAIT="${LIST_WAIT:-30}"
offline=false
[ "${1:-}" = "--offline" ] && offline=true

die() { echo "setup.sh: $*" >&2; exit "${2:-1}"; }
console_step() {
  cat >&2 <<'EOF'
setup.sh: the rooms are not there yet. One Console step:
  Switch Console -> Templates -> run quarantine.template.yaml (room intake, Mode B)
  and quarantine-unsafe.template.yaml (room intake-a, Mode A), then re-run ./setup.sh
EOF
  exit 2
}

[ -r "$CONF_DIR/quarantine.env" ] || die "missing $CONF_DIR/quarantine.env (see README: Prerequisites)"
# shellcheck disable=SC1090,SC1091
. "$CONF_DIR/quarantine.env"

api() {  # api METHOD PATH [JSON]
  local method="$1" path="$2" body="${3:-}"
  if [ -n "$body" ]; then
    curl -fsS -X "$method" -H "Authorization: Bearer $MM_USER_TOKEN" \
      -H 'Content-Type: application/json' -d "$body" "$MM_URL/api/v4$path"
  else
    curl -fsS -X "$method" -H "Authorization: Bearer $MM_USER_TOKEN" "$MM_URL/api/v4$path"
  fi
}

check_room() {  # check_room ROOM READER FIXER
  local room="$1" reader="$2" fixer="$3" cid post t0 deadline reply
  cid="$(api GET "/teams/name/$MM_TEAM/channels/name/$room" 2>/dev/null | jq -r '.id // empty')" || true
  [ -n "$cid" ] || console_step
  post="$(api POST /posts "$(jq -nc --arg c "$cid" '{channel_id:$c, message:"!list-agents"}')")"
  t0="$(jq -r .create_at <<<"$post")"
  deadline=$(( $(date +%s) + LIST_WAIT ))
  while [ "$(date +%s)" -lt "$deadline" ]; do
    sleep 2
    reply="$(api GET "/channels/$cid/posts?since=$t0" | jq -r --argjson t "$t0" \
      '[.posts[] | select(.create_at > $t) | .message] | join("\n")')"
    if grep -qw -- "$reader" <<<"$reply" && grep -qw -- "$fixer" <<<"$reply"; then
      echo "setup.sh: room $room lists $reader and $fixer"
      return 0
    fi
  done
  die "room $room: !list-agents did not list $reader and $fixer within ${LIST_WAIT}s (is the Switch server running?)"
}

if [ "$offline" = false ]; then
  [ -r "$CONF_DIR/mattermost.env" ] || die "missing $CONF_DIR/mattermost.env (see README: Prerequisites)"
  # shellcheck disable=SC1090,SC1091
  . "$CONF_DIR/mattermost.env"
  : "${MM_URL:?}" "${MM_TEAM:?}" "${MM_USER_TOKEN:?}"
  curl -fsS -m 5 "$MM_URL/api/v4/system/ping" >/dev/null ||
    die "Mattermost at $MM_URL does not answer (start the server in Switch Console)"
  check_room intake reader fixer
  check_room intake-a reader-a fixer-a
fi

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
  if [ ! -d "$dest/.git" ]; then
    (cd "$HERE/toyrepo" && tar --exclude __pycache__ --exclude .pytest_cache \
      --exclude canary.txt -cf - .) | (cd "$dest" && tar -xf -)
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
echo "setup.sh: fixtures and seeded toyrepo in place for both modes"
