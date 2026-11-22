---
tags: [skill-creator]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I'm starting a Lean formalization of a paper in geometric functional analysis with the formalize-math-paper skill. The proof of its main theorem cites the Kahane–Khintchine inequality for Banach spaces (Hytönen, van Neerven, Veraar and Weis, Analysis in Banach Spaces, Vol. II) twice, with the constants it gives, and once uses that L^p(ℝ) has the UMD property. As far as I know none of this is in Mathlib, and Mathlib has no theory of Banach-space-valued Rademacher sums or of UMD spaces; building it might take several thousand lines. How should the formalization handle these cited results? Don't fetch anything or create any repository; write your plan to plan.md.
