# architecture principles

## model the domain

put the real domain in a data structure, not in conditions spread across files. the right structure makes bad states impossible and removes branches. it is cheap to choose when you write the code, and expensive to recover later.

reach for:

- a state machine, not scattered booleans or phase checks.
- a typed model, not loose parameters or the same shape assumed in many files.
- a map, registry, lookup table or tagged union, not branches spread across files.
- a reducer or a command and event model, not ad hoc mutation.
- a module built around one body of domain knowledge, not a sequence like load, validate, transform, save. order of execution is not ownership.
- a queue, cache, index, tree or graph when the access pattern calls for one.

do not force it. if the current shape is clear, local and unlikely to grow, keep the boring code.

**signs you skipped this:** a new feature adds one more branch to an existing if/else chain. a second boolean must stay in sync with the first. modules named after phases repeat the same rules.

## boundary discipline

check data at system boundaries. trust it inside.

- **at boundaries** (cli args, config files, external apis, network, environment variables): validate, return errors, handle bad input.
- **inside the system:** typed data, errors that propagate, no second validation.
- **across a boundary:** expose domain concepts, not the transport, storage or framework types.
- keep business logic in pure functions with no framework in them. the shell around them stays thin.

**the tests:** "is this data crossing a boundary right now?" if not, the check is extra. "can this be a pure function that the shell calls?" if yes, extract it.

## type system discipline

make the compiler reject bad states, mixed-up values and unhandled cases.

- **make bad states impossible to write.** use sum types (tagged unions, enums with data), not a bag of optional fields. `{ done: boolean; doneAt?: Date }` allows `done: true` with no date. use `{ kind: 'open' } | { kind: 'done'; at: Date }`. if you need a comment to say which field combinations are valid, split it into a sum type.
- **build types from the values you want,** not by cutting a loose type down with checks. a non-empty list is a head plus a rest.
- **brand values that mean different things.** a `UserId` and an `OrderId` are both strings, but they must not mix. give each its own type and validate once when you create it.
- **external data has no type until you parse it.** json, rpc payloads, cli args, env vars, database rows. parse each one into the typed model at the boundary.
- **do not lie to the compiler.** each cast (`as`, `any`, a non-null assertion) is a crash waiting to happen. prove the fact, or move the check to the boundary.
- **make matches exhaustive,** so a new case breaks the build where it is not handled (`never` in typescript, `match` in rust).
- **derive types from the schema that owns the shape** (openapi, protobuf, graphql, migrations). do not hand-write a parallel type.
- **make a type stronger only where code would otherwise fail.** a "should never happen" throw shows where a type is too weak. fix that one, then stop.

## make operations idempotent

an operation that changes state must reach the same end state no matter how many times it runs, or where the last run stopped.

ask three questions:

1. what happens if this runs twice in a row?
2. what happens if the last run crashed at any point?
3. does running again reach the same end state?

if any answer is "it depends on what was left behind", add a step that reconciles state: scan what exists, clean what is stale, adopt what is live. compare by content, not by creation order. detect stale locks by process id.

## migrate callers, then delete the old api

when you decide a new internal api is right, move every caller and delete the old api in the same change. do not keep both.

- list the callers, move them, delete the old path.
- a temporary adapter is an exception with an end date, not the default.
- update tests to assert the new contract. delete tests that only protect old internals.

this holds when no outside user depends on the old api. two paths for one job make the code harder to change and teach the next agent the wrong way.

## separate before you serialize shared state

when two actors may write the same thing (a file, a branch, a key, an object), first ask if they need to share it at all.

1. find the shared state: files both read and write, branches both push to.
2. **default: remove the shared target.** give each actor its own file, key or branch, and merge only when you read or report. two workers that each write their own field into one `state.json` still share a file. `indexer-state.json` and `metrics-state.json` do not.
3. only when one shared target is a real invariant, serialize access with structure: a lock file, a single writer, sequential phases, compare-and-swap. instructions and conventions are not concurrency control.
