---
tags: [skill-creator]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

My repository formalizes two papers on quasiconvexity, each in its own directory, following the formalize-math-paper skill. Paper B's main proof uses the main theorem of paper A, which is already fully proved in the repo. The two papers also define quasiconvexity slightly differently: paper A tests it with smooth compactly supported maps on a domain, paper B with Lipschitz maps on the unit cube that vanish on the boundary. Paper B also has a remark that its theorem together with paper A's settles every case except one, and I'd like that combined statement formalized too. Should paper B's library state paper A's theorem as an axiom among its cited results (Common/External/)? How should I handle the two definitions, and where does the combined statement go? Write your recommendation to answer.md; don't create anything else.
