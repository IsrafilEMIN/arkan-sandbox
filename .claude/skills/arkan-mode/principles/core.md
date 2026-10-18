# core principles

## laziness protocol

- **make the smallest change that solves the problem.** fewer lines beat "elegant" boilerplate.
- **keep each decision in one place.** do not repeat the same choice in several files. put it behind one source of truth and pass the result as a simple value.
- before you add an abstraction, a layer or a new parameter that threads through many calls, ask if the problem needs it. usually it does not.

## subtract before you add

remove complexity first, then build. leave the design a little simpler than you found it.

- remove before you construct. delete dead code, extra validators and stale references first.
- cut before you polish. reach the minimum before you spend effort on quality.
- design for the use you can see, not for edge cases you imagine.
- add no validator, parser or guard that the spec does not ask for.
- when a file or section has nothing new to say, delete it. do not leave a stub.

## foundational thinking

structural decisions keep options open. code-level decisions keep code simple.

- **data structures first.** define the core types early. trace every way the data is read and written. choose structures that fit the main paths.
- **at code level, remove repeated structure, not every repeated line.** three similar lines are better than an early abstraction. prefer explicit code over clever code.
- **concurrency.** before two actors share state, ask "what happens if the other one changes this at the same time?" if the answer is not "nothing", isolate it.
- **scaffold first.** if something helps every later phase (ci, lint, test setup, shared types), do it first. setup before features, tests before fixes.
- each step adds one clear abstraction, or deepens one that exists. do not spread a new capability across callers as special cases.

## redesign from first principles

when you add a requirement to an existing design, do not bolt it on. design as if the requirement was there from the start.

1. read every affected file and understand the current design.
2. ask: "if we wrote this from scratch with this requirement, what would we build?"
3. carry the change through every reference: types, docs, examples, comments that give reasons.
4. think about the whole redesign, then deliver it in small steps.

## attack the premise

when two or more fixes that share one premise fail the same check, suspect the premise, not the fixes.

1. **write the premise down.** it is the one sentence that every failed fix assumed.
2. **count before the next fix.** measure the problem per actor (per worker, per request type, per file). write the count as a script you can run again.
3. **read the skew.** if the same few actors hold most of the problem every run, something gives them that role. find what gives it. that is your next "why".
4. **remove the imbalance; do not compensate for it.** move, rotate or randomize the role. a retry path or a rebalance step leaves the cause in place.

if the count is even across actors, the premise is not the cause. look elsewhere, and keep the count as evidence.

## minimize reader load

maintainability is the work a reader must do to understand the code. it has two parts: **layers to trace** (steps between the question and the answer) and **state to hold** (hidden or changing context the reader must remember).

- collapse layers that cost more than they save: a wrapper with one caller, an adapter with one implementation, an indirection nobody needed.
- a layer must change the abstraction. a layer that repeats the same methods and arguments only adds load.
- prefer interfaces that hide real decisions behind a small surface.
- shrink the scope of state: returns over mutation, locals over fields, fields over module state, module state over globals. derive values instead of syncing them.
- state an invariant once, at the boundary, not in every consumer.

**the test:** can a new reader answer "where does x come from?" and "what can change x?" in 30 seconds? if not, cut layers or cut state.

## experience first

when ease of building conflicts with what the user feels, choose the user.

- every feature, control and option must earn its place.
- ship fewer features, finished well.
- prototype before you commit. a design choice is cheaper in throwaway code.
- get the details right: feedback, error states, spacing, transitions.
- the user is whoever consumes the work: the end user of an app, the developer who imports a library, the next engineer who maintains the code.

## exhaust the design space

for a new interaction or architecture with no example in the codebase, build two or three competing options and compare them side by side before you commit. this also holds for product decisions where the answer depends on how it feels, not on logic.

## build the lever

when the work is not trivial, build the tool that does it, instead of doing it by hand. a script, codemod or generator does the work the same way every time, and a reviewer can read it and run it again.

- do the first unit by hand to learn the recipe. then build the tool, run it on that unit, and diff against your hand-made result.
- make the tool safe to run twice.
- one script that handles every unit beats many subagents that each edit by hand.
- when you send work to subagents, write the recipe, the check and the "do not touch" list into one file they all read.
- if you say you used this principle and there is no script, codemod or check in the diff, you did not use it.
- build the smallest script that does the job, never a framework.

## outcome-oriented execution

in a planned rewrite or migration, aim for the end state. do not write temporary compatibility code just to keep every middle step perfect.

- planned, scoped breakage in the middle is fine when you can undo it.
- say where breakage is allowed.
- keep strong checks on the areas you touch while you migrate.
- run every static and runtime check at the end.
