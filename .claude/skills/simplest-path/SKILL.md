---
name: simplest-path
description: Check a plan or build for overengineering and find the simplest thing that meets the goal. Use before a multi-step build, when scope keeps growing, or when the user asks "are we overengineering?", "is this the simplest/best way?", "why is this so long?".
---

# Simplest path

As simple as possible, as complicated as needed. Complexity must be paid for by a named requirement or a measured failure.

## Restate the goal

Write the user's goal in one line, in their words. Example: "stash, fetch, rebase, pop, push, and a clear message if it fails." Every part of the plan is judged against that line.

## Look for existing machinery

Before building, check what already does the job: the tool's own command, an existing protocol in the codebase, a documented config option, an existing script in the repo. Reuse beats reinvention. Say which existing piece you reuse.

## Risk-to-cost ladder

For each safeguard or feature in the plan, place it on the ladder:

1. **Eliminate** the risk, if the cost is small.
2. **Minimize** it, if elimination costs too much.
3. **Accept** it, and write down that it is accepted, if minimizing costs too much.

A safeguard whose cost exceeds the damage it prevents comes out.

## Honest answer

When the user asks "are we overengineering?", answer yes or no first. Then list what to cut, what to keep, and why. If the work already grew past the goal, stop, show the scope that grew, and propose the smaller version before writing more code.

## Size check

Before implementing, state the expected size of the change (files, lines, new tests). If the real diff grows far past that, pause and report.
