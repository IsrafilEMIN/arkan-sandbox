# Issue tracker: GitHub

Issues and specs for this repo live as GitHub issues. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --title "..." --body "..."`. Use a heredoc for multi-line bodies.
- **Read an issue**: `gh issue view <number> --comments`, filtering comments by `jq` and also fetching labels.
- **List issues**: `gh issue list --state open --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'` with appropriate `--label` and `--state` filters.
- **Comment on an issue**: `gh issue comment <number> --body "..."`
- **Apply / remove labels**: `gh issue edit <number> --add-label "..."` / `--remove-label "..."`
- **Close**: `gh issue close <number> --comment "..."`

Infer the repo from `git remote -v`; `gh` does this automatically when run inside a clone.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(Set to `yes` if this repo treats external PRs as feature requests; `/triage` reads this flag.)_

When set to `yes`, PRs run through the same labels and states as issues, using the `gh pr` equivalents:

- **Read a PR**: `gh pr view <number> --comments` and `gh pr diff <number>` for the diff.
- **List external PRs for triage**: `gh pr list --state open --json number,title,body,labels,author,authorAssociation,comments` then keep only `authorAssociation` of `CONTRIBUTOR`, `FIRST_TIME_CONTRIBUTOR`, or `NONE` (drop `OWNER`/`MEMBER`/`COLLABORATOR`).
- **Comment / label / close**: `gh pr comment`, `gh pr edit --add-label`/`--remove-label`, `gh pr close`.

GitHub shares one number space across issues and PRs, so a bare `#42` may be either: resolve with `gh pr view 42` and fall back to `gh issue view 42`.

## When a skill says "publish to the issue tracker"

Create a GitHub issue. Then apply the board **Add** operation (see [Board](#board)).

## When a skill says "fetch the relevant ticket"

Run `gh issue view <number> --comments`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **child** issues as tickets.

- **Map**: a single issue labelled `wayfinder:map`, holding the Notes / Decisions-so-far / Fog body. `gh issue create --label wayfinder:map`.
- **Child ticket**: an issue linked to the map as a GitHub sub-issue (`gh api` on the sub-issues endpoint). Where sub-issues aren't enabled, add the child to a task list in the map body and put `Part of #<map>` at the top of the child body. Labels: `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, the ticket is assigned to the driving dev.
- **Blocking**: GitHub's **native issue dependencies**, the canonical, UI-visible representation. Add an edge with `gh api --method POST repos/<owner>/<repo>/issues/<child>/dependencies/blocked_by -F issue_id=<blocker-db-id>`, where `<blocker-db-id>` is the blocker's numeric **database id** (`gh api repos/<owner>/<repo>/issues/<n> --jq .id`, _not_ the `#number` or `node_id`). GitHub reports `issue_dependencies_summary.blocked_by` (open blockers only, the live gate). Where dependencies aren't available, fall back to a `Blocked by: #<n>, #<n>` line at the top of the child body. A ticket is unblocked when every blocker is closed.
- **Frontier query**: list the map's open children (`gh issue list --state open`, scoped to the map's sub-issues / task list), drop any with an open blocker (`issue_dependencies_summary.blocked_by > 0`, or an open issue in the `Blocked by` line) or an assignee; first in map order wins.
- **Claim**: `gh issue edit <n> --add-assignee @me`, the session's first write. The card does not move.
- **Resolve**: `gh issue comment <n> --body "<answer>"`, then `gh issue close <n>`, then the board **Resolve** operation, then append a context pointer (gist + link) to the map's Decisions-so-far.

## Board

`TODO.md` at the repo root is this repo's Tern board. Tern reads `##` headings as lanes and `- [ ]` items as cards, writes every change to the file at once, and shows edits from other programs live. Git tracks `TODO.md`, and the copy on `main` is the only board. A card change goes in the same branch and PR as the work that causes it, and reaches `main` only after that PR's checks pass and the merge is verified. Nobody commits `TODO.md` straight to `main`, and an edit made in Tern goes through a PR too. When a skill changes a ticket's state, it also applies the matching board operation below, in that branch. If no work branch exists, for example for a ticket published outside a PR, open a branch and PR for the board change alone.

The GitHub issue is the source of truth; the card mirrors it. A card holds only its title, its tags and one note line. Every detail lives in the issue. If a card and its issue disagree (for example, someone edited the issue on the web or ticked a card in Tern), fix the card from the issue and tell the user.

- **Lanes**: `## Backlog`, `## Todo`, `## Done`, in that order. If a lane is missing, add it.
- **Card**: `- [ ] <n>: <title> #<feature-slug>`, then `#<role>` when triage labels are configured, `#<type>` for a wayfinder ticket, `#spec` for a spec, and `📅 YYYY-MM-DD` only when the ticket has a due date. Under the card, one indented note line: `<issue url> · blocked by: <refs, or none>`. `<n>` is the issue number without `#`, because Tern reads `#…` as a tag.
- **Ready**: a ticket is ready when it is open, nobody has claimed it, and every ticket that blocks it is closed. If `docs/agents/triage-labels.md` exists, its role must also be `ready-for-agent` or `ready-for-human`. Wayfinder tickets carry a type, not a triage role, so the role condition does not apply to them. A `#spec` card is never ready: it stays in `Backlog` until it is resolved.
- **Claimed**: a ticket is claimed while a pushed branch or an open PR does its work, or while it has an assignee in a tracker that has assignees. The board never shows a claim: a lane on `main` shows only a state that passed the pipeline.
- **Lane rule**: `Done` if the ticket is closed; else `Todo` if it is ready; else `Backlog`. A claim does not move the card.
- **Done is always ticked**: Tern marks every card in `Done` as done. A ticket closed without the work (`wontfix`, out of scope) goes to `Done` ticked, with a `#wontfix` tag.

Operations:

- **Add** (a ticket or spec is published): in the branch that publishes it, add its card to the lane the lane rule picks. Keep each blocker's card above the cards it blocks.
- **Resolve** (the ticket closes): in the branch that does the work, tick the card and move it to `Done`. Then apply the lane rule again to each card this ticket blocked. No card moves to `Todo` while any of its blockers is still open.
- **Change role**: replace the `#<role>` tag, then apply the lane rule again to that card.
- **Worktrees**: each branch edits only the cards of its own tickets. If two PRs conflict on `TODO.md`, the later one rebases on `main`, keeps both changes, and passes its checks again before it merges.
