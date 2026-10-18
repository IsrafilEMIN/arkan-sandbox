---
name: post-merge
description: "After a merged change breaks main: find the bad merge, make main safe, and ticket the miss."
disable-model-invocation: true
---

A merged change broke something. You make main safe, then turn the **miss** (the bug that got past the task loop) into a ticket a person can act on. Run each step in order; each ends on its criterion.

## Steps

1. **Read the repo's setup.** Read `docs/agents/issue-tracker.md` (and `docs/agents/triage-labels.md` if it exists) for where tickets go and how they are published. Find the check that shows the break: the failing CI job's command, or the test, build or verify step the person names. _Done when_ you can run that check locally and name the tracker. If the repo has no `docs/agents/issue-tracker.md`, ask the person where the ticket goes.

2. **Read the signals.** The person may name the break. Also read what the repo has: CI runs on main (`gh run list --branch <main>`), error logs or alerts it exposes, revert commits (`git log -i --grep=revert`), open incident issues. Classify a CI failure before you trust it: flake earns one fresh run, and an identical second failure is real. _Done when_ you have one confirmed failure and its check exits non-zero on main's head. If nothing is broken, report the signals you read and stop.

3. **Find the first bad commit.** Pick the last commit where the check passes, then bisect along main's merges only: `git bisect start --first-parent <bad> <good>`, then `git bisect run <check>`. Read the merge back (`gh pr view <pr> --json state,mergedAt,baseRefName`, or `git log -1 <sha>`) so the ticket names the PR that really landed. Run `git bisect reset` after. _Done when_ the check fails on that commit and passes on its first parent.

4. **Make main safe.** On a new branch from main, choose whichever is safer, faster:
   - **revert**: `git revert -m 1 <merge>` (no `-m` for a squash commit). The fallback whenever a fix is unclear.
   - **fix forward**: a small change, red first, through `tdd`, when the cause is plain and a revert would undo more than it saves.

   _Done when_ the check passes on the branch, the repo's other checks still pass, and the branch is pushed. Open the PR with the `pr` skill. Merging is the person's call.

5. **Name the node that should have caught it.** Walk the task loop in order: build + `tdd` (a test for this case), prove (tests, build, lint, verify), `code-review`, `security-review`. Pick the first node that had what it needed to catch the bug, and say what it lacked: a missing test, a check that never ran, a rule the reviewer does not hold. _Done when_ the answer cites evidence from the bad diff or the node's own output, not a guess.

6. **Ticket the miss.** Publish one ticket on the repo's tracker, as `docs/agents/issue-tracker.md` says, with the `needs-triage` role if the repo uses triage labels. It holds: the bad merge (SHA and PR), the confirmed bug (the check and its failing output), the revert or fix PR, and step 5's answer. If the miss needs a look back over the session that made it, say so in the ticket and suggest `retro`. _Done when_ the ticket exists and its link or path is in your reply.

## Reply

The signal, the first bad commit, the revert or fix PR, the node that should have caught it, and the ticket.
