# Issue tracker: Local Markdown

Issues and specs for this repo live as markdown files in `.scratch/`.

## Conventions

- One feature per directory: `.scratch/<feature-slug>/`
- The spec is `.scratch/<feature-slug>/spec.md`
- Implementation issues are one file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`, numbered from `01`, never a single combined tickets file
- Triage state is the `#<role>` tag on the ticket's card in `TODO.md` (see `triage-labels.md` for the role strings), and the card's lane is the ticket's status (see [Board](#board)). A ticket is closed when its card is in `Done`.
- Comments and conversation history append to the bottom of the file under a `## Comments` heading

## When a skill says "publish to the issue tracker"

Create a new file under `.scratch/<feature-slug>/` (creating the directory if needed), then apply the board **Add** operation (see [Board](#board)).

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. The user will normally pass the path or the issue number directly.

## Wayfinding operations

Used by `/wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `.scratch/<effort>/map.md` (the Notes / Decisions-so-far / Fog body).
- **Child ticket**: `.scratch/<effort>/issues/NN-<slug>.md`, numbered from `01`, with the question in the body. A `Type:` line records the ticket type (`research`/`prototype`/`grilling`/`task`). The card's lane records resolved (`Done`); the pushed work branch records the claim.
- **Blocking**: a `Blocked by: NN, NN` line near the top. A ticket is unblocked when the card of every ticket it lists is in `Done`.
- **Frontier**: the cards in `Todo` tagged `#<effort>`; the first one on the board wins.
- **Claim**: create and push the ticket's work branch before any work. The card does not move.
- **Resolve**: append the answer under an `## Answer` heading, apply the board **Resolve** operation, then append a context pointer (gist + link) to the map's Decisions-so-far in `map.md`.

## Board

`TODO.md` at the repo root is this repo's Tern board. Tern reads `##` headings as lanes and `- [ ]` items as cards, writes every change to the file at once, and shows edits from other programs live. Git tracks `TODO.md`, and the copy on `main` is the only board. A card change goes in the same branch and PR as the work that causes it, and reaches `main` only after that PR's checks pass and the merge is verified. Nobody commits `TODO.md` straight to `main`, and an edit made in Tern goes through a PR too. When a skill changes a ticket's state, it also applies the matching board operation below, in that branch. If no work branch exists, for example for a ticket published outside a PR, open a branch and PR for the board change alone.

The ticket file is the source of truth; the card mirrors it. A card holds only its title, its tags and one note line. Every detail lives in the ticket file. The card's lane and its `#<role>` tag are the ticket's status. Ticket files carry no `Status:` line.

- **Lanes**: `## Backlog`, `## Todo`, `## Done`, in that order. If a lane is missing, add it.
- **Card**: `- [ ] <NN>: <title> #<feature-slug>`, then `#<role>` when triage labels are configured, `#<type>` for a wayfinder ticket, `#spec` for a spec, and `📅 YYYY-MM-DD` only when the ticket has a due date. Under the card, one indented note line: `<path to the ticket file> · blocked by: <refs, or none>`. `<feature-slug>` is the `.scratch/` directory name.
- **Ready**: a ticket is ready when it is open, nobody has claimed it, and every ticket that blocks it is closed. If `docs/agents/triage-labels.md` exists, its role must also be `ready-for-agent` or `ready-for-human`. Wayfinder tickets carry a type, not a triage role, so the role condition does not apply to them. A `#spec` card is never ready: it stays in `Backlog` until it is resolved.
- **Claimed**: a ticket is claimed while a pushed branch or an open PR does its work, or while it has an assignee in a tracker that has assignees. The board never shows a claim: a lane on `main` shows only a state that passed the pipeline.
- **Lane rule**: `Done` if the ticket is closed; else `Todo` if it is ready; else `Backlog`. A claim does not move the card.
- **Done is always ticked**: Tern marks every card in `Done` as done. A ticket closed without the work (`wontfix`, out of scope) goes to `Done` ticked, with a `#wontfix` tag.

Operations:

- **Add** (a ticket or spec is published): in the branch that publishes it, add its card to the lane the lane rule picks. Keep each blocker's card above the cards it blocks.
- **Resolve** (the ticket closes): in the branch that does the work, tick the card and move it to `Done`. Then apply the lane rule again to each card this ticket blocked. No card moves to `Todo` while any of its blockers is still open.
- **Change role**: replace the `#<role>` tag, then apply the lane rule again to that card.
- **Worktrees**: each branch edits only the cards of its own tickets. If two PRs conflict on `TODO.md`, the later one rebases on `main`, keeps both changes, and passes its checks again before it merges.
