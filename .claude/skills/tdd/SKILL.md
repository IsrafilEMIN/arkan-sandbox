---
name: tdd
description: Test-driven development engine. Use when the user wants to build features or fix bugs test-first, mentions "red-green-refactor", or wants integration tests.
user-invocable: false
---

# Test-Driven Development

TDD is the red → green loop. This skill is the engine: what each cycle must produce and the traps to avoid while running it. The suite policy lives in the `test-to-break` skill.

When exploring the codebase, read `GLOSSARY.md` (if it exists) so test names and interface vocabulary match the project's domain language, and respect ADRs in the area you're touching.

## Policy check, before the first cycle

The suite policy lives in the `test-to-break` skill (file: `../test-to-break/SKILL.md`): portfolio, seam agreement, assertion validity, restraint.

If the seams are not agreed, or the change adds a workflow or decision node, read that file now and settle the policy with the user before writing the test.

If the change is one clear failure at an agreed seam, run the loop directly.

## What a good test is

Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't. A good test reads like a specification: "user can checkout with valid cart" tells you exactly what capability exists, and it survives refactors because it doesn't care about internal structure.

See [tests.md](tests.md) for examples and [mocking.md](mocking.md) for mocking guidelines.

## Anti-patterns

- **Implementation-coupled**: mocks internal collaborators, tests private methods, or verifies through a side channel (querying the database instead of using the interface). The tell: the test breaks when you refactor but behavior hasn't changed.
- **Tautological**: the expected value restates the code's own computation, so the test can never disagree with the code. The rule is in the `test-to-break` policy.
- **Horizontal slicing**: writing all tests first, then all implementation. Bulk tests verify _imagined_ behavior: you test the _shape_ of things rather than user-facing behavior, the tests go insensitive to real changes, and you commit to test structure before understanding the implementation. Work in **vertical slices** instead: one test → one implementation → repeat, each test a **tracer bullet** that responds to what the last cycle taught you.

## Rules of the loop

- **Red before green.** Write the failing test first, then only enough code to pass it. Don't anticipate future tests or add speculative features.
- **One slice at a time.** One seam, one test, one minimal implementation per cycle.
- **Refactoring is not part of the loop.** It belongs to the review stage (see the `code-review` skill), not the red → green implementation cycle.
