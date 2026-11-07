---
tags: [skill-creator]
max_turns: 30
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

We split the general part of our Lean formalization of Smith and Jones, 'Spectral gaps of random regular graphs' (repository github.com/alice/lean4-spectral-gaps), into a package of its own. It proves the Perron-Frobenius theorem for nonnegative irreducible matrices: files PerronFrobenius/Basic.lean and PerronFrobenius/Irreducible.lean, about 2,000 lines, written by Claude (Opus 5.5) in Claude Code for us; the maintainer is Alice Doe. One file, PerronFrobenius/Collatz.lean, adapts code from Bob Roe's repository bob/linalg-extras (MIT licence). The package will be published as github.com/alice/lean4-perron-frobenius, on Lean v4.36.0-rc2 and Mathlib v4.36.0-rc2, Apache-2.0. The main theorem is PerronFrobenius.exists_pos_eigenvector. Write its README.md (just the file; don't create anything else).
