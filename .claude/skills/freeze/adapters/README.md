# freeze adapters

One policy, many harnesses.

`scripts/freeze-guard.sh` holds all the policy. Each adapter here is a thin
shim: it takes a tool call, calls the guard, and turns the guard's answer into
the harness's block signal.

## arm it

Run the guard from the project directory.

```
~/.agents/skills/freeze/scripts/freeze-guard.sh arm ~/work/project
~/.agents/skills/freeze/scripts/freeze-guard.sh status
~/.agents/skills/freeze/scripts/freeze-guard.sh disarm
```

`arm <dir>` freezes writes to `<dir>` for the project at `$PWD`. The state file
is `${FREEZE_STATE_DIR:-$HOME/.agents/state/freeze}/<key>`. The key is `pwd -P`
with every `/` replaced by `%`. The file holds one canonical absolute directory
path.

Writes under the frozen directory pass. Everything else blocks. `disarm`
deletes the state file. No state file means allow all.

Hook mode keys off the `cwd` in the payload when the harness sends one, and
falls back to the process `pwd`. Arm from the same directory the harness runs
in, or the keys will not line up.

## the contract the adapters rely on

```
freeze-guard.sh hook        # hook JSON on stdin; exit 2 = block, reason on stderr
```

`hook` reads the tool input from stdin and exits `2` to block. `0` allows. It
needs `jq`. Without `jq` it allows and warns, because fail-open is safer than a
half-parsed gate.

## adapter matrix

| harness | file / step | where it goes | mid-session toggle? | covers shell writes? | status on this machine |
| --- | --- | --- | --- | --- | --- |
| claude code | add a `PreToolUse` command hook, `"$HOME/.agents/skills/freeze/scripts/freeze-guard.sh" hook`, matcher `Write\|Edit` | `~/.claude/settings.json` | no, restart to reload | only if you add `Bash` to the matcher; then best-effort | manual. `install.sh` only symlinks the skill into `~/.claude/skills/freeze`. |
| oh-my-pi (omp) | `adapters/freeze.ts` | `~/.omp/agent/hooks/pre/freeze.ts` | yes, state changes apply on the next tool call | yes, best-effort | `install.sh` symlinks it. |
| pi | `adapters/freeze.ts` | `~/.pi/agent/extensions/freeze.ts` | yes, state changes apply on the next tool call | yes, best-effort | `install.sh` symlinks it. |
| codex | `adapters/codex-hooks.json`, merged into the `hooks` object | `~/.codex/hooks.json` | no, hooks load at session start | yes, best-effort | `install.sh` merges the entry and backs up to `hooks.json.bak-freeze`. codex asks you to review and trust a new hook before it runs. |
| hermes | `adapters/hermes-config.yaml`, the `hooks:` block | the profile `config.yaml`, for example `~/.hermes/profiles/<name>/config.yaml` | no, next CLI session or gateway restart | yes, best-effort | not applied. `install.sh` only names the file. Paste the block yourself, then approve the hook on first use. |
| grok | `adapters/grok-hooks.json` | `~/.grok/hooks/freeze.json` | yes, `Space` in the Hooks tab toggles it; `r` reloads from disk | yes, best-effort | `install.sh` symlinks it. Global `~/.grok/hooks/*.json` are always trusted. |
| anything else | run the guard, then obey it | your own hook or wrapper | depends on you | depends on you | recipe below. |

## anything else: the two-line recipe

Before a tool call, run the guard with the tool call on stdin. Treat exit `2` as
a block and show stderr to the model.

```sh
printf '%s' "$TOOL_CALL_JSON" | ~/.agents/skills/freeze/scripts/freeze-guard.sh hook
# exit 2 -> block; stderr holds the reason
```

Keep `jq` on `PATH`, or the guard fails open.

## per-harness notes

claude code reads `.tool_input` and blocks on exit `2`. The hook block ships in
the skill's own frontmatter; copy it into your settings if you want it on
`Bash` as well.

codex honors exit `2` as a block and reads `.tool_name` and `.tool_input` from
stdin. Matcher `Bash|apply_patch|Edit|Write` covers shell calls and file edits.
`apply_patch` carries the patch text in `tool_input.command`, so the guard reads
the path from each `*** Add|Update|Delete File:` envelope line. `Move to:` lines
and bare hunks are not checked. Docs: <https://learn.chatgpt.com/docs/hooks>.

omp and pi share one extension API. The adapter also registers a `/freeze`
command, so you can arm and disarm without leaving the session.

hermes runs shell hooks as subprocesses and blocks a `pre_tool_call` hook that
exits `2`. It asks for consent once per event and command pair. Consider adding
`fail_closed: true` so a crashed or timed-out guard blocks instead of allowing.
Docs: <https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/hooks.md>.

grok tests the matcher against its own tool name and maps claude aliases:
`Bash` maps to `run_terminal_command`, and `Edit`, `Write`, and `MultiEdit` map
to `search_replace`. A matcher keeps the original name too, so the shipped
matcher `Bash|Write|Edit|MultiEdit|search_replace|run_terminal_command` fires
either way. grok's stdin is camelCase: `toolName`, `toolInput`, `cwd`. grok also
merges hooks from `~/.claude/settings.json` and `~/.cursor/hooks.json`. Docs:
the bundled `~/.grok/docs/user-guide/10-hooks.md`.

## caveat

Every hook adapter here is a guardrail, not a wall. Only an OS sandbox is
containment.

- A crashed, timed-out, or misconfigured hook may fail open. codex, grok, and
  hermes all fail open by default. The block only holds when the guard runs to
  completion and returns its answer.
- Shell coverage is best-effort. The guard reads the obvious write targets in a
  command: `>`, `>>`, `2>`, `&>`, `tee`, `sed -i`, and `apply_patch` envelope
  lines. It never tries to be a shell parser. An obfuscated command can slip
  past it.
- A harness that spawns writes through another tool, or through a nested agent,
  can route around a hook that only watches the tools you configured.

Use a container or a filesystem sandbox when you need a real boundary.
