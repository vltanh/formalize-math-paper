# Credits: how the formalization was made

`CREDITS.md` says how the formalization was made, from the run log and the session transcripts
(SKILL.md, Run log). The README's credits sum it up in two or three bullets and link to it
(`audit-report.md`, Section 3, item 6). Write it in bullets, with one section for each round of
work: the first formalization, then each later round that the user asked for.

```markdown
# Credits

How this formalization was made, from the run log and the session transcripts.

## Who
- **Author and maintainer:** <the people; who asked for the formalization and chose its scope>
- **Formalization:** <each AI system: the model(s), and the agent and harness, with their versions;
  how many sessions; who wrote the draft, if there was one>
- **Procedure:** <this skill, with a link to its repository and its version or commit>
- **Review:** <whether a person has reviewed the proofs; which independent agents checked what>

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
