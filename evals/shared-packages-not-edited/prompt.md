---
tags: [skill-creator]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

My Lean project, set up with the formalize-math-paper skill, requires a package of mine, lean4-convexity, at its published commit. The build fails because one lemma in that package has an implicit argument that Lean can't infer at my call site. To save disk space, my local checkouts share .lake/packages through hard links. The quickest fix seems to be editing the lemma directly in .lake/packages/Convexity. Is that OK? Write the steps you would take to answer.md; don't change anything else.
