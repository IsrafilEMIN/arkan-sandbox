---
name: product-brief
description: Write, review or trim a product brief and keep it separate from specs and ADRs. Use when the user creates or reviews a brief, asks "is this too detailed for a brief", wants to go through a brief line by line, or asks how brief, spec and ADR differ.
disable-model-invocation: true
---

# Product brief

A brief says **what** we build and **why**, for whom, and how we know it worked. A spec says **how it behaves**. An ADR says **why we chose one way over another**.

Test for each line: if it would still be true after a refactor and describes behavior, it belongs in the spec. If someone would ask "why not X?", the answer belongs in an ADR. If neither, and it states intent, users, outcomes, principles, non-goals or risks, it belongs in the brief.

## Brief shape

Overview -> problem -> what it does for the user -> success metrics -> principles -> non-goals -> MVP scope (one or two lines) -> risks. Short. No architecture, tools, protocols, or numbers that only an engineer needs.

## Line-by-line review

When the user says "print it, let's go line by line":

1. Print the brief with line numbers.
2. Go section by section. For each line flag only: belongs elsewhere (say where), too narrow or too broad, unclear, duplicated.
3. Number the questions so the user can answer "L3 yes, L5 cut".
4. Apply exactly the answers. Keep any synced file (for example `AGENTS.md` principles) in step and say what you synced.

## Out-of-date docs

When the user says the spec and ADRs are intentionally out of date, judge the brief on its own and collect spec/ADR follow-ups in a separate list for later.
