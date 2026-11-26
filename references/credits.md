# Credits: how the formalization was made

## 1. The run log

Keep the run log that SKILL.md describes ("Run log") from Phase 0; the milestone commits also record
when each phase ends.

From the log, report the elapsed time to the audited formalization: from the start to the commit
that completes `REPORT.md` (`CREDITS.md`, which reports this time, comes in a later commit). Also
report the number of sub-agents and the most that ran at once, their total working time, and their
tool calls and tokens (output, input and cache reads, separately). Where the platform keeps session
transcripts, take these figures from them: the summaries shown when an agent finishes may measure
something else. For Claude Code, `scripts/session_stats.py` computes them. Pass every transcript if
the work spanned several sessions, and `--until` with the time of the commit that completes
`REPORT.md`. When the user asks for more work later, log each round the same way, and get its
figures with `--since` and `--until` at its start and end. Put the figures in `CREDITS.md`, one
section per round (Section 2), and in `formalization.yaml` (`automation.methods`:
`models`, `framework`, `tool_setup`, `cost`). Put the elapsed time and the number of running agents
in status reports.

With several papers in one repository, each paper's `CREDITS.md` reports the rounds spent on that
paper, and the umbrella README sums them up in one line per paper and round (`multi-paper.md`,
Section 6).

## 2. `CREDITS.md`

`docs/PaperName/CREDITS.md` says how the formalization was made, from the run log and the session
transcripts (Section 1). The README's credits sum it up in a few bullets and link to it
(`audit-report.md`, Section 3, item 8). Write it in bullets, with one section for each round of
work: the first formalization, then each later round that the user asked for.

```markdown
# Credits

How this formalization was made, from the run log and the session transcripts.

## Who
- Author and maintainer: <the people; who asked for the formalization and chose its scope>
- Formalization: <each AI system: the model(s), and the agent and harness, with their versions;
  how many sessions; who wrote the draft, if there was one; the main session's model in each
  round, if it changed>
- Procedure: <this skill, with a link to its repository and its version or commit>
- Review: <whether a person has reviewed the proofs; which independent agents checked what, with
  their models>

## <Round> (<dates>)
<For a later round, what the user asked for.>

How it was made:
- <each step and who did it: the statements and their review, the proofs (how many sub-agents,
  and what each kind did), the audit and its review, the integration and the checks>

Figures, from <the start, with date, time and time zone> to <the end: for the first formalization,
the commit that completes REPORT.md>:
- elapsed time;
- sub-agents: how many, the most that ran at once, and their total working time;
- tool calls, and tokens with output, input and cache reads counted separately (they differ by
  orders of magnitude), for the sub-agents and for the main session;
- model calls, by model.
<Give only what the platform records, and say what the figures leave out, such as pauses between
the user's requests or agents not counted.>
```
