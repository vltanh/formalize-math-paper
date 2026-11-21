---
tags: [skill-creator]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I already have a finished Lean formalization of one paper on a famous open problem (it uses the formalize-math-paper layout: Basic/, External/, the paper's library in Smith/, Challenge.lean and Solution.lean at the root, comparator.json, formalization.yaml, README.md, REPORT.md, CREDITS.md). Now I want to formalize two more papers on the same problem in the same repository: one settles a complementary case, the other is a sequel to the first paper. They should share code where it makes sense, but I want each paper to be submittable to Palomar on its own and to have its own docs, plus one central document for the whole problem. How should I organize the repository, and in what order should I do the reorganization? Write the plan to answer.md; don't create anything else.
