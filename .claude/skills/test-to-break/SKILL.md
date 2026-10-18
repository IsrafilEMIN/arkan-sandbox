---
name: test-to-break
description: Suite strategy for tests - plan, audit, list, or prune; the policy the tdd engine reads when the suite shape is unsettled.
user-invocable: false
---

# Test to break

The purpose of a test is to break the system and say exactly where it broke. A suite that only confirms what it just set up proves nothing.

This skill is the policy layer for tests. The `tdd` engine reads it when a build session starts without a settled suite shape. Run it by hand to plan, audit, list, or prune a suite.

## Seams: where tests go

A **seam** is the public boundary you test at: the interface where you observe behavior without reaching inside. Tests live at seams, never against internals.

**Agree the seams before any test.** Write down the seams under test and confirm them with the user. No test is written at an unconfirmed seam. You can't test everything, so agreeing the seams up front lands the testing effort on the critical paths and complex logic instead of every edge case.

Ask: "What's the public interface, and which seams should we test?"

When the shape of that interface is itself in question (how deep the module is, where the seam belongs, what the interface should expose), consult the `codebase-design` skill for the vocabulary: module, interface, depth, seam, adapter, leverage, locality. It is a reference to consult, not a session to run.

## Two kinds, nothing else

- **Positive end-to-end.** One per intended workflow, run through the whole chain with realistic mixed input (for an inbox: newsletter, personal mail, reply-owed, exception mail, all in one inbox, through to the final user-visible result and the stored state). These prove the system does its job.
- **Negative per node.** For each decision node, the ways it can fail or be fooled: bad input, timeout, wrong time window, missing data, stale state, duplicate run. Each test fails with a message that names the node and the cause. These prove every failure is caught and reported.

Everything else is overlap. If two suites cover the same path, keep the one closer to real use and delete the other.

## Each assertion

- Compares against an expected value written in the test, never against a value the code under test produced.
- Can fail. Mutate the code (flip the condition, remove the guard) and confirm the test goes red.

## Listing tests

When the user asks what tests exist, group by node and give one plain-English line per test: what situation it builds and what it proves. Name the gaps: nodes with no negative test, behavior that is only tested with fakes, judgment calls a model makes that no deterministic test can grade.

## Restraint

Add tests when the user asks or when a fix needs a reproducing test. When the user says "tests later", stop adding tests and say what is untested.
