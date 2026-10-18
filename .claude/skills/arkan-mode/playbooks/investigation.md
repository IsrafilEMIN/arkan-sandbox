### Investigation

**You own the answer. Plan, route, write.**

Investigation requests are read-only. They produce a cited explanation or a recommendation, not a code change.

1. Read the affected code. Give wide reads to a subagent and keep its summary (see **Subagents** in `SKILL.md`). For motivation questions, also read the history: `git log`, `git blame`, and the PRs and tickets that touched the code.
2. Produce this output: Overview / Key Concepts / How It Works / Where Things Live / Gotchas. If the request is a decision between alternatives, give a recommendation with a tradeoffs table instead.
3. Write the reply per **The reply** in `SKILL.md`.

No PR, no babysit, no design sketch unless the investigation precedes a code change. If it does, hand back to the user and re-route to Bug fix or Feature.

**Reply:** the investigation output. For "are we sure?" answers, include your real judgment with reasons. Push back if the premise is wrong (see **Autonomy** in `SKILL.md`).
