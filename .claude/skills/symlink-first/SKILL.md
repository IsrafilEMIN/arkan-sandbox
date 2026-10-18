---
name: symlink-first
description: Keep one canonical copy of shared material and symlink every other location to it. Use when the user adds or installs a skill, an AGENTS.md, a config, a dotfile or a script that more than one tool, agent or project reads, or asks to dedupe copies or fix broken links.
user-invocable: false
---

# Symlink first

Each shared file or folder has one **canonical** copy. Every other location is a **mirror**: a symlink to the canonical copy. A change is a one-place edit, and no copy can drift. This is the default of the `npx skills` CLI ([vercel-labs/skills](https://github.com/vercel-labs/skills)): "symlinks from each agent to a canonical copy. Single source of truth, easy updates."

Link only where a tool cannot read the canonical copy itself. A link that a tool does not need is a second path to the same item, and the tool can load it twice.

## Agent map

The global canonical home is `~/.agents/`: `~/.agents/AGENTS.md` and `~/.agents/skills/<name>/`. Verified 2026-10 against each tool's docs or source:

| agent | reads `~/.agents/skills/` | global instructions |
| --- | --- | --- |
| claude code | no: link `~/.claude/skills/<name>` | link `~/.claude/CLAUDE.md` |
| codex 0.161 | yes | link `${CODEX_HOME:-~/.codex}/AGENTS.md` |
| pi 1.1 | yes | link `~/.pi/agent/AGENTS.md` |
| omp 18.8 | yes | reads `~/.agents/AGENTS.md` itself |
| dsh 0.2 | yes (`$DSH_AGENTS_HOME`) | link `${DSH_HOME:-~/.dsh}/AGENTS.md` |
| opencode 2.0 | yes | not checked |
| cursor 2026.09 | yes | not checked |
| hermes 0.21 | through config: `skills.external_dirs: [~/.agents/skills]` in `~/.hermes/config.yaml` | not checked |

Codex also reads `$CODEX_HOME/skills/` (its `.system` skills and its own installer use it), so a link there shows a skill twice. Omp, opencode and cursor also load `~/.claude/skills/` (omp and cursor also `~/.codex/skills/`), so they can see the claude code links too. That cost is accepted: claude code has no other path.

Hermes gets `external_dirs`, never links: its curator treats an external skill as read-only, but it can edit a linked skill and so write into the canonical copy. A local hermes skill with the same name wins over the external one.

If a tool version changes, check its docs before you trust a row.

## Procedure

1. **Pick the canonical home.**

   | material | canonical home |
   | --- | --- |
   | global skill or instruction | `~/.agents/` (see [Agent map](#agent-map)) |
   | project skill or instruction | `<repo>/.agents/skills/<name>/`, `<repo>/AGENTS.md` |
   | script that two skills use | the skill that owns the behaviour; the other skill links to it |
   | local package that two projects use | a workspace package (`workspace:*`, `pnpm` store), never a vendored copy |

2. **Write the material in the canonical home.**

3. **Link the global mirrors.** For global material, run the script. It creates every missing link in the agent map and changes nothing else:

   ```bash
   "$HOME/.agents/skills/symlink-first/scripts/link-agents.sh"
   ```

   Use `--check` to report without a change. The script skips an agent whose home folder does not exist. It also skips each skill in its `claude_builtin` list: claude code ships that skill itself, so a link makes a duplicate. For project material, link by hand with a relative target inside the repo: `ln -sn ../.agents/skills/<name> .claude/skills/<name>`.

4. **Resolve each report line.** The step is done when the script prints `ok` and exits 0.
   - `COPY ... identical`: delete the copy, then run the script again.
   - `COPY ... differs`: merge the differences into the canonical copy first. If the merge is not obvious, show the diff to the user and ask.
   - `CONFLICT`: the link points to a different target. Show it to the user.
   - `DANGLING`: the canonical skill is gone. Delete the link, or restore the skill.

5. **Confirm each tool loads the item**: the skill list, or the instruction file.

## Skill metadata for codex

Every global skill has `agents/openai.yaml` beside its `SKILL.md`. Claude code reads invocation from the `SKILL.md` frontmatter; codex reads it from this file ([codex skills docs](https://learn.chatgpt.com/docs/build-skills), verified 2026-10). Keep the two in agreement:

```yaml
interface:
  display_name: "Skill Name"
  short_description: "One line a human reads in the skill picker"
policy:
  allow_implicit_invocation: false
```

- `policy.allow_implicit_invocation: false` goes in if and only if `SKILL.md` has `disable-model-invocation: true`. For a model-invoked skill, leave out the `policy` block: the codex default is `true`.
- The script reports `NO-OPENAI-YAML` for a skill without the file and `POLICY-MISMATCH` when the two invocation settings disagree. Write or fix the file, then run the script again.

## Link granularity

Link each item, never the whole tool directory. A tool directory also holds tool-owned state (sessions, auth, `~/.claude/skills/synced`, `~/.codex/skills/.system`), and a whole-directory link mixes that state into the canonical tree.

## When to copy

Copy only at a boundary that a link cannot cross. Each case below is a real breakage, not a preference:

- **Atomic writers.** A tool that saves through a temp file and a rename replaces the link with a regular file. Link only files that you author. Leave tool-written files (`settings.json`, state files) as regular files. After the tool writes, check with `test -L`.
- **Packaging boundaries.** A Docker build context, an `npm publish` tarball, a zip, a cloud sync folder and a remote sandbox do not follow a link out of their tree. Resolve the links at build time (`cp -L`, `rsync -L`) and keep the source tree linked.
- **Links out of a repo.** A link from a repo to `~` dangles for every other clone. Keep repo links inside the repo. Git stores links natively; on Windows, set `git config core.symlinks true` and enable Developer Mode.
- **A file that must diverge.** If one tool needs extra lines, use its import syntax on top of the canonical file (`@AGENTS.md` in a `CLAUDE.md`) and keep the extra lines in the importing file.

## Installer-managed skills

`npx skills add` makes the canonical copy and the mirror links itself. Keep its symlink default. Use `--copy` only for a case in [When to copy](#when-to-copy). The CLI owns `~/.agents/.skill-lock.json`; change it only through the CLI.
