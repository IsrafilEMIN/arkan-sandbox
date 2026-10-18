# Issue tracker: GitLab

Issues and specs for this repo live as GitLab issues. Use the [`glab`](https://gitlab.com/gitlab-org/cli) CLI for all operations.

## Conventions

- **Create an issue**: `glab issue create --title "..." --description "..."`. Use a heredoc for multi-line descriptions. Pass `--description -` to open an editor.
- **Read an issue**: `glab issue view <number> --comments`. Use `-F json` for machine-readable output.
- **List issues**: `glab issue list -F json` with appropriate `--label` filters.
- **Comment on an issue**: `glab issue note <number> --message "..."`. GitLab calls comments "notes".
- **Apply / remove labels**: `glab issue update <number> --label "..."` / `--unlabel "..."`. Multiple labels can be comma-separated or by repeating the flag.
- **Close**: `glab issue close <number>`. `glab issue close` does not accept a closing comment, so post the explanation first with `glab issue note <number> --message "..."`, then close.
- **Merge requests**: GitLab calls PRs "merge requests". Use `glab mr create`, `glab mr view`, `glab mr note`, etc., the same shape as `gh pr ...` with `mr` in place of `pr` and `note`/`--message` in place of `comment`/`--body`.

Infer the repo from `git remote -v`; `glab` does this automatically when run inside a clone.

## Merge requests as a triage surface

**MRs as a request surface: no.** _(Set to `yes` if this repo treats external merge requests as feature requests; `/triage` reads this flag.)_

When set to `yes`, MRs run through the same labels and states as issues, using the `glab mr` equivalents:

- **Read an MR**: `glab mr view <number> --comments` and `glab mr diff <number>` for the diff.
- **List external MRs for triage**: `glab mr list -F json`, then keep only MRs whose author is not a project member/owner (a contributor's MR, not a maintainer's in-flight work).
- **Comment / label / close**: `glab mr note`, `glab mr update --label`/`--unlabel`, `glab mr close`.

Unlike GitHub, GitLab numbers issues and MRs separately, so `#42` is unambiguous once you know which surface the maintainer means.

## When a skill says "publish to the issue tracker"

Create a GitLab issue. Then apply the board **Add** operation (see [Board](#board)).

## When a skill says "fetch the relevant ticket"

Run `glab issue view <number> --comments`.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a single issue with **child** issues as tickets.

- **Map**: a single issue labelled `wayfinder:map`, holding the Notes / Decisions-so-far / Fog body. `glab issue create --label wayfinder:map`. (On GitLab tiers with native epics, an epic may hold the map instead; a labelled issue works everywhere.)
- **Child ticket**: an issue carrying `Part of #<map>` at the top of its description and labels `wayfinder:<type>` (`research`/`prototype`/`grilling`/`task`). Once claimed, the ticket is assigned to the driving dev.
- **Blocking**: GitLab's **native blocking link**, the canonical, UI-visible representation. Add it with the `/blocked_by #<n>` quick action, posted as a note (`glab issue note <child> --message "/blocked_by #<blocker>"`). Native blocking links are a Premium/Ultimate feature; on the free tier (or where unavailable) fall back to a `Blocked by: #<n>, #<n>` line at the top of the description. A ticket is unblocked when every blocker is closed.
- **Frontier query**: `glab issue list -F json` scoped to the map's children, drop any with an open blocker: a native `blocked_by` link to an open issue (`glab api projects/:id/issues/:iid/links`), or an open issue in the `Blocked by` line, or an assignee; first in map order wins.
- **Claim**: `glab issue update <n> --assignee @me`, the session's first write. The card does not move.
- **Resolve**: `glab issue note <n> --message "<answer>"`, then `glab issue close <n>`, then the board **Resolve** operation, then append a context pointer (gist + link) to the map's Decisions-so-far.

## Board

`TODO.md` at the repo root is this repo's Tern board. Tern reads `##` headings as lanes and `- [ ]` items as cards, writes every change to the file at once, and shows edits from other programs live. Git tracks `TODO.md`, and the copy on `main` is the only board. A card change goes in the same branch and PR as the work that causes it, and reaches `main` only after that PR's checks pass and the merge is verified. Nobody commits `TODO.md` straight to `main`, and an edit made in Tern goes through a PR too. When a skill changes a ticket's state, it also applies the matching board operation below, in that branch. If no work branch exists, for example for a ticket published outside a PR, open a branch and PR for the board change alone.

The GitLab issue is the source of truth; the card mirrors it. A card holds only its title, its tags and one note line. Every detail lives in the issue. If a card and its issue disagree (for example, someone edited the issue on the web or ticked a card in Tern), fix the card from the issue and tell the user.

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
