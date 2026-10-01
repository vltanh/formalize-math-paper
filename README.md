# formalize-math-paper

A [Claude Code](https://claude.com/claude-code) skill for formalizing a mathematics research paper
in Lean 4 with Mathlib, in any field of mathematics. It guides the work end to end:

- read the paper and record its results, constants, citations and suspected typos;
- set up a Lean project on current Mathlib, using the module system;
- state every result first, and check each statement against the paper's TeX source;
- prove everything the paper proves (Stage 1), then every result it cites (Stage 2), until the
  project has no `sorry` and no `axiom`;
- verify: the axioms of every declaration, and Comparator;
- write `REPORT.md`, an audit of the paper against the formalization (errors and gaps, missing
  and redundant hypotheses, how the paper uses each cited result), and `README.md`;
- clean up warnings, and package the project for the [Palomar](https://palomar-registry.org)
  registry (Challenge/Solution, `comparator.json`, `formalization.yaml`, preflight).

It also covers turning an existing, never-compiled Lean draft into a project that builds.

## Install

```sh
git clone https://github.com/vltanh/formalize-math-paper ~/.claude/skills/formalize-math-paper
```

Claude Code picks the skill up on its own. Ask it to formalize a paper (an arXiv link is
enough), to make a Lean draft compile, or to prepare a Lean project for Palomar.

## Contents

| Path | Contents |
| --- | --- |
| `SKILL.md` | The workflow: principles, rules, phases and completion gates |
| `references/` | Detailed guides: Lean project setup, parallel repair with subagents, the audit report, Palomar packaging, cleanup |
| `scripts/` | Helpers: checking one file, `sorry`-ing failing proofs, converting to the module system, statement diffs, removing unused hypotheses, linking documentation to the code, checking Markdown tables |
| `assets/` | Templates: the axiom and dependency audit (`Audit.lean`), the CI workflow, the Palomar preflight workflow |

## Example

[lean4-graham-rearrangement-conjecture](https://github.com/vltanh/lean4-graham-rearrangement-conjecture)
formalizes H. T. Pham and L. Sauermann, *On Graham's rearrangement conjecture*, with this
workflow. It started from an uncompiled draft and ended with a passing Palomar preflight.
