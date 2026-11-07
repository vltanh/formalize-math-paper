---
tags: [skill-creator]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

I'm about to start a Lean 4 formalization of a paper on Nash equilibria of mean-field games. Its main existence proof uses Kakutani's fixed-point theorem for set-valued maps, which as far as I know isn't in Mathlib, and the formalization would have to prove it (probably a couple of thousand lines, including Brouwer). Before we write any Lean: how should the project be organized, and where should Kakutani's theorem go? Don't fetch anything or create any repository; just write your plan to plan.md.
