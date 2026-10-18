---
name: handoff
description: Compact the current conversation into a handoff block of markdown for another agent to pick up. Use when the user asks for a handoff, or when work pauses mid-task and a fresh session must resume it (the pause-safely playbook).
---

Write a handoff summarising the current conversation so a fresh agent can continue the work. Output it in the chat as one fenced markdown block that the user can copy. Do not write a file.

Include a "suggested skills" section in the block, naming which skills the next agent should call the Skill tool for.

Do not duplicate content already captured in other artifacts (specs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the handoff accordingly.
