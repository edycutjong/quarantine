# Friction log: building QUARANTINE on Switch

> **Draft.** Notes for the Switch team, kept as I hit things. Each entry gives what happened,
> where the docs or tracker cover it, and the workaround I used. Entries found during the live
> runs are added as they happen.

## Known issues I designed around before writing code

| What | Reference | Workaround in this repo |
|---|---|---|
| Switch's Mattermost adapter drops agent replies that exceed the post-size limit; the only trace is a server log line (reported from code reading) | [sandbox-quantum/switch#1580](https://github.com/sandbox-quantum/switch/issues/1580) | Every agent's instructions cap replies at 5 short lines (`quarantine*.template.yaml`) |
| The activity card for a template's kickoff turn can be rejected with "Invalid RootId" and retried with no limit | [sandbox-quantum/switch#1158](https://github.com/sandbox-quantum/switch/issues/1158) | Kickoff is one plain sentence (`@reader say hi in one line.`), and neither the demo nor the bench depends on the kickoff or its card |
| Console can leave template `{params}` unfilled inside managed agents' instructions | [sandbox-quantum/switch#1577](https://github.com/sandbox-quantum/switch/issues/1577) | No `{...}` tokens anywhere in an `instructions:` block; only `directory:` uses `{$agents_dir}` |

## Found while building

| What | Reference | Workaround |
|---|---|---|
| The `{agent}` placeholder only resolves in a template with a single `agent:`. A two-agent room (`agents:` list) has to spell out every name and directory | `TEMPLATES.md` placeholder table (`{agent}`: "In a document with a single `agent:`") | Literal names `reader`/`fixer` (and `reader-a`/`fixer-a`) with `directory: "{$agents_dir}/<name>"` |
| Agent names are unique per server, so the same room can't run twice with only `addressing` changed | `getting-started/onboard-your-agents` ("unique across the whole server") | Two templates, `intake` (Mode B) and `intake-a` (Mode A); `tests/test_template_diff.py` asserts they differ only by the `-a` suffix and the fixer's `addressing:` word |
| Starting the local server is a Console (GUI) action; I found no CLI or API call that starts it headlessly | `getting-started/add-a-server` ("Switch Console starts it") | Documented under "What you need" in `DEMO.md`; running the two templates (DEMO §1) is also a Console step. `setup.sh`, the bench and the DEMO §3 runs are scripted (REST posts as `@user`) |
| Running a template headlessly needs a Gateway session: `POST /gateway/rooms/from-template-document` takes the cookie from `POST /gateway/auth/login` (email + password); I found no token-based path for an operator script | Gateway OpenAPI (`/gateway/openapi.json`); `identity-and-access` (Gateway = session cookie carrying a JWT) | Log in once in-process, never store the password in the repo; the server fills `{$agents_dir}` itself, so the same two template files work unchanged |
| An agent's progress ("Queued…", "Working…", "Worked for 8s. 2 tool calls.") is posted as a thread reply to the order, by the agent's own account, so "first post by the reader after the order" is not its answer | observed in the live rooms (`evidence/live-transcript.json`) | `bench/inject.sh` counts only top-level posts and skips status, session-start and room-document notices |
