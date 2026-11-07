# Packages of their own

A formalization sometimes has to prove a theorem that no Lean library has and that others would
import on its own. Such a development can be a Lake package of its own, in its own repository,
required by the project at a pinned commit. The default is not to split: keep general mathematics
in `Basic/` and cited results in `External/` (SKILL.md, Phase 2).

## 1. The bar

Propose a package of its own only when **all** of these hold:

- **Famous by name.** It proves a theorem, or a small theory around one, that mathematicians outside
  the paper's area know by name. A lemma that only this paper needs, however long, does not
  qualify.
- **Missing.** Neither Mathlib nor another maintained public Lean library has it, and no Mathlib
  pull request for it is close to merging.
- **Substantial.** It is not one quick contribution to Mathlib: several hundred lines or more, or a
  theory of its own that the proof builds on.
- **General.** Its statements say nothing about the paper's objects, and it imports only Mathlib
  and other such packages.
- **Reusable.** Someone outside this project could plausibly import it.

Otherwise it stays in `Basic/` or `External/`, and small general lemmas are offered to Mathlib,
the long-term home of general mathematics. Expect at most one or two packages for a paper, often
none. Decide during the inventory (Phase 1), so that the code is written in the package from the
start. The user decides whether to split, the name, the visibility and when to publish; creating
and pushing a repository needs permission (Rules).

## 2. One package per area

Name a package for its area, not for one theorem (`lean4-<area>`, not `lean4-<theorem>`), so that
related results can join it later instead of starting more repositories. Inside it, give each
theorem its own directory (`<Area>/<Theorem>/`). Before proposing a new package, check whether an
existing one is the right home.

## 3. The package stands alone

- It is a Lake package with the project's `lean-toolchain` and Mathlib release, the module system,
  Mathlib's style, its own README (what it proves, with the exact statements; the method and its
  references; how to depend on it; credits: its maintainers, and the AI systems that wrote it, as
  the Rules require), licence, CI and axiom audit.
  Its library globs are `<Area>.*` (Lake's `.+` would skip the root file). To avoid rebuilding
  Mathlib, hard-link the project's `.lake/packages` and copy the Mathlib entries of its manifest.
- It carries no provenance. It says what it proves and on which mathematical sources, not what it
  was written for, who asked for it, where its files came from, or how it was made. Nothing in it
  refers back to the project that motivated it (the paper, its objects or authors, the project's
  repository or paths), in no README, docstring, comment, name or commit message.

## 4. Depending on it

- The project requires it by `path = "../lean4-<area>"` while it is developed, and by its published
  commit (`git = …`, `rev = "<full commit hash>"`) before the project is pushed; run
  `lake update <Area>` alone, so that Mathlib's pin does not move. A project and its packages
  share one Mathlib revision.
- A cited result keeps its place in the project: `External/` states it in its source's terms and
  proves it from the package. The route check and the audit treat it like any other cited result.
- The project's README, `REPORT.md` (Section 2) and `formalization.yaml` say where it uses the
  package; the dependency runs one way.
- Palomar restricts only the Challenge's imports (`references/palomar.md`, Section 1): the Solution
  may depend on the package, even when the package is registered as an entry of its own.
