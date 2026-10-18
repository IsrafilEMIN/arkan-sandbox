---
name: assess
description: Read-only mode that finds the problem and the possible solutions without acting.
---

# Assess

A question is a request for an answer, not a request for action. In this mode the deliverable is a report. The system state after the turn is identical to the state before it. When debugging, name the root cause and say whether each fix removes it or patches a symptom.

## Rule

Do not run any action that writes or changes state until the user gives an explicit go.

## Deep research

If the answer needs more than a quick look (many sources, external docs, fast-moving tools), read `research.md` in this skill's directory and use it as the engine. Follow its steps 1–3. Skip steps 4–5: do not write a file. Put the labeled, cited findings in the report.

## Report shape

1. **Answer** the exact question in one or two sentences.
2. **Evidence** for each claim: file:line, command output, or doc link. Mark inference as inference.
3. **Proposals**, numbered, so the user can answer "1 yes, 2 no".
