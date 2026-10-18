# principles for working with agents

## guard the context window

a full context window makes reasoning worse, and compaction loses detail.

- send bulk work to subagents: wide searches, long logs, large files, long transcripts. keep only their summaries in your own context.
- size each phase. limit the files per phase, and count what each tool call costs.
- read the part of a file you need, not the whole file, when you know where to look.
- do not read the same large output twice. save it to a file and search the file.

## never block on the human

the human checks in now and then. you must stay unblocked.

- do it, then show it. do not ask "should i do x?". do x, and say why.
- when you see a problem, note it and fix it in the next round.
- reversible actions go ahead: write code, edit notes, split tasks, open a draft pr.
- actions no one can undo still need a yes: force-push, delete production data, deploy, send an outside message.
- product direction comes from the human. execution does not wait for them.

## encode lessons in structure

when you write the same instruction a second time, or the user corrects the same mistake twice, make the rule part of the code: a lint rule, a type, a test, a runtime check or a script. text is the weakest fix, because nothing fails when an agent skips it.

- if the fix is structural, use only the structural fix. the instruction was the symptom.
- if the lesson needs judgment and cannot be encoded, make the instruction more visible and add an example of the failure.
- the `retro` skill runs this on a whole session, when a person starts it.
