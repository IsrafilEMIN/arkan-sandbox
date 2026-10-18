---
name: freeze
description: Freeze writes to one directory so every edit stays inside it, with a pre-tool-use guard that blocks writes outside the frozen directory. Use when the user says freeze <dir>, wants to lock edits to a directory, or asks to stop writes outside a path.
disable-model-invocation: true
hooks:
  PreToolUse:
    - matcher: "Write|Edit"
      hooks:
        - type: command
          command: "\"$HOME/.agents/skills/freeze/scripts/freeze-guard.sh\" hook"
---

# Freeze

Freeze writes to one directory. The guard script allows edits under the frozen directory. It blocks writes outside it. The same script serves every harness through a thin adapter.

## Procedure

1. Arm the freeze on the target directory.

```bash
"$HOME/.agents/skills/freeze/scripts/freeze-guard.sh" arm $ARGUMENTS
```

`$ARGUMENTS` is the directory from the user request. If it is empty, ask for the directory.

2. Edit only files under the frozen directory. The guard blocks any other target.

3. Check the state at any time.

```bash
"$HOME/.agents/skills/freeze/scripts/freeze-guard.sh" status
```

4. Lift the freeze when the work is done.

```bash
"$HOME/.agents/skills/freeze/scripts/freeze-guard.sh" disarm
```

The freeze is per project. The state key is the resolved project directory (`/` becomes `%`). The state file holds one absolute directory path.

## Harness wiring

| harness | wiring | how you arm it | covers shell writes? |
| --- | --- | --- | --- |
| claude-code | the frontmatter `hooks` block in this file. it registers when you type `/freeze`. copy the same block into settings.json to keep it on in every session | `/freeze <dir>`, then the skill runs the arm command | best-effort |
| omp | `install.sh` links `adapters/freeze.ts` to `~/.omp/agent/hooks/pre/freeze.ts`. the extension also registers a `/freeze` command | `/freeze <dir>` in the session | best-effort |
| pi | `install.sh` links the same file to `~/.pi/agent/extensions/freeze.ts` | `/freeze <dir>` in the session | best-effort |
| codex | `install.sh` merges `adapters/codex-hooks.json` into `~/.codex/hooks.json` | run the arm command, or ask in chat | best-effort |
| grok | `install.sh` links `adapters/grok-hooks.json` into `~/.grok/hooks/` | run the arm command, or ask in chat | best-effort |
| hermes | paste `adapters/hermes-config.yaml` into the hermes config | run the arm command, or ask in chat | best-effort |

`install.sh` links what it can and prints the steps it cannot do. The hook stays inert until a state file exists. A harness with no command registration is armed by running the arm command, or by asking in chat. Read the snippets in `adapters/`.

## Limits

- The guard checks the file tools of the harness only. Read tools pass untouched.
- Bash writes are a best-effort text check. The guard reads `>`, `>>`, `2>`, `&>`, `tee`, and `sed -i` targets. It also reads `*** Add File:`, `*** Update File:`, and `*** Delete File:` lines from a codex `apply_patch` payload. A quoted path with a space, a variable, or a command substitution can hide a target.
- A subprocess write is invisible. A program that opens a file itself never reaches the guard.
- Path checks handle `..` and symlinks. The guard resolves the deepest existing ancestor of each target, then re-appends the rest. A textual compare alone cannot do this.
- This is a seatbelt, not a sandbox. It stops a mistaken edit. It does not stop a determined process.
