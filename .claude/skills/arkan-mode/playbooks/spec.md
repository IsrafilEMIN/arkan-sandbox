### Spec

**You own the integration branch. Run each ready ticket as its own task loop, merge it, and land the spec as one PR.**

The tickets are not a list of steps. They are a **task graph**: each ticket lists the tickets that block it, so there is always a **frontier** of tickets ready to start. A ticket joins the frontier when it passes the gate in step 0 of `SKILL.md` (role `ready-for-agent`, ready by the issue tracker doc's rule) and every ticket that blocks it is merged to the integration branch. Tickets tagged `ready-for-human` or `needs-info` wait, and so does everything they block.

Talk to subagents through context pointers: the spec, the ticket paths, the notes files, the commits. Do not paste what a pointer already holds. Run implementer subagents in the background where the harness supports it, for the most work at once.

1. Read the spec and its tickets, and write down the task graph: each ticket, its blockers, its role. Name the first frontier, and each ticket that waits and why.
2. (optional) Send an **exploration subagent** to read what the tickets need: codebase files, external docs. It saves its notes as markdown in a folder outside the repo that every later subagent can read, so the implementers build instead of explore.
3. Create the integration branch from the main branch. If the issue tracker closes work through PRs, or the user asks for one, open a draft PR after the first merge in step 5 (a branch with no commits ahead of main cannot open one), marked as closing the spec and its tickets.
4. Start one **implementer subagent** per frontier ticket, each in its own worktree on its own branch, all at once. Do not build a ticket in this chat, however small: this chat runs the playbook. Each implementer:
   - confirms its worktree is based on the integration branch tip, and resets onto it if not;
   - reads `SKILL.md` and runs the task loop on its one ticket: claim it, check it in step 0, match a playbook, build with `tdd`, prove it. It skips the code review and the PR: the spec has one of each, in steps 7 and 8;
   - merges the integration branch tip into its own branch, and proves it again, before it reports done.
5. When an implementer reports done, read its diff yourself, then merge its branch into the integration branch with a **merger subagent**. An implementer that reports a missing blocker (step 0 of `SKILL.md`) gets no merge: its ticket leaves the frontier until that blocker merges.
6. A merge can unblock tickets. Each ticket whose blockers are now all merged, and that passes the gate, joins the frontier: start an implementer for it at once (step 4). Repeat steps 4 to 6 until the frontier is empty.
7. Once every ticket is merged, run the `code-review` skill on the integration branch in a fresh context. Fix every issue it raises in a single implementer subagent, then run the full test suite.
8. If a draft PR exists, mark it ready for review and drive it with **Opening a PR**. Otherwise, resolve each ticket the way the issue tracker closes work, and report the integration branch.
9. Clean up every implementer worktree.

**Reply:** the task graph, which tickets ran in parallel, which waited and why, what the review found and how it was fixed, and the PR link or the integration branch.
