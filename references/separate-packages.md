# Packages of their own: when a result deserves its own repository

A formalization sometimes has to prove a famous theorem that no Lean library has: a fixed-point
theorem, the Pontryagin maximum principle, a classical packing theorem. Such a development can
become a Lake package of its own, published as its own repository, which the project then requires
at a pinned commit. Done well, others can import it and it outlives the paper. Done too often, it
leaves a scatter of small repositories, each needing its own CI, Mathlib bumps and maintenance, and
a project that a reader has to assemble from many places. **The default is not to split.** Keep
general mathematics in `Basic/` and cited results in `External/` (SKILL.md, Phase 2), and offer
small general lemmas to Mathlib. Split only what clears the bar below, and only with the user's
agreement.

## Contents

1. The bar
2. One package per area
3. Mathlib first
4. When to decide
5. How to build it
6. Publishing and depending on it
7. Palomar

## 1. The bar

Propose a package of its own only when **all** of these hold:

- **Famous by name.** The development proves a theorem, or a small theory around one, that
  mathematicians outside the paper's area know by name and would look for: Brouwer's fixed-point
  theorem, the Pontryagin maximum principle, Fejes Tóth's theorem on lattice packings. A lemma
  that only this paper needs, however long, does not qualify.
- **Missing.** Neither Mathlib nor another maintained public Lean library has it, and no Mathlib
  pull request for it is close to merging (search Mathlib, its open pull requests, the Lean Zulip
  and GitHub; Phase 0, "earlier work").
- **Substantial.** It is large enough (as a rule of thumb, several hundred lines or more, often
  thousands) that it is not one quick contribution to Mathlib, or it needs infrastructure of its own
  (for the maximum principle: ODEs with measurable controls, needle variations).
- **General.** Its statements say nothing about the paper's objects, and it can import only
  Mathlib and other such packages. If it needs the paper's definitions, it is not general.
- **Reusable.** Someone outside this project could plausibly import it.

When a candidate fails one of these, it stays in `Basic/` or `External/`. Expect at most one or two
packages for a paper, and often none. If the list of candidates grows longer, group them (Section
2) or keep them in the project.

## 2. One package per area

Name a package for its area, not for one theorem, so that related results can join it later instead
of starting more repositories: `lean4-fixed-point` (Brouwer now; Kakutani and Schauder later), not
`lean4-brouwer`; `lean4-optimal-control` (the maximum principle with Filippov's existence theorem
and the ODE toolkit they share), not one repository for each. Inside it, give each theorem its own
directory (`FixedPoint/Brouwer/`, `FixedPoint/Kakutani/`). Before proposing a new package, check
whether an existing one, the user's or the project's earlier ones, is the right home.

## 3. Mathlib first

Mathlib is the long-term home of general mathematics. A package is for a development too large or
too specialized to contribute now, or a staging area on the way to Mathlib. Small general lemmas
(an inequality, a measurability lemma, a planar convexity theorem of a hundred lines) go to `Basic/`
with Mathlib's names, and `Basic/README.md` says where in Mathlib each could go. Write a package's
code in Mathlib's style (names, docstrings, line length), so that it can be contributed later.

## 4. When to decide

Decide during the inventory (Phase 1), when the citations are surveyed: a cited result whose proof
needs a large general development is the typical candidate. Propose it to the user with the bar
above, the proposed name, what goes in, and the cost. Deciding early means writing it as a package
from the start; extracting it later means renaming modules, moving files and changing imports
across the project, best done when no other work is in flight. If the user declines, the
development goes to `Basic/` or `External/` and can still be split later.

The user decides: whether to split, the repository's name, its visibility (public is required for
the project's CI and for Palomar to fetch it without tokens), and when to publish (for example only
once it is sorry-free; until then the project depends on it by a local path and cannot be pushed,
since a path outside the repository does not build elsewhere). Creating the repository and pushing
to it are actions that others can see (SKILL.md, Rules).

## 5. How to build it

- A sibling directory of the project (`../lean4-fixed-point`), with its own `lakefile.toml` (Lake
  package and library named for the area, in PascalCase, for example `FixedPoint`), the project's
  `lean-toolchain` and the same Mathlib release tag, so that the two can be used together.
- In `lakefile.toml`, `globs = ["FixedPoint.*"]`: Lake's `.+` matches only submodules, so the
  root file would not be built.
- The module system, as in the project (`references/lean-project.md`, Section 3).
- Its own `README.md` (what it proves, with the exact Lean statements; the method and its
  references; how to depend on it; credits as in the project, `references/credits.md`: people as
  authors and maintainers, AI systems credited in the README only), `LICENSE` (the project's, unless
  the user chooses otherwise), `.gitignore` (`/.lake`), a CI workflow (build, axiom audit) and an
  axiom audit script like the project's.
- To avoid rebuilding Mathlib, hard-link the project's packages:
  `cp -al ../Project/.lake/packages .lake/` and copy the Mathlib entries of the project's
  `lake-manifest.json`; check that `lake build` builds only the package's own modules.
- A cited result keeps its place in the project: `External/` states it in its source's terms, says
  where it comes from, and proves it from the package (or the Solution uses the package's theorem
  directly). The route check and the audit treat it like any other cited result.

## 6. Publishing and depending on it

- With the user's permission, create the repository (`gh repo create <owner>/<name> --public
  --source . --remote origin --push`), check that its CI passes and that GitHub detects the licence
  (`gh api repos/<owner>/<name>/license --jq .license.spdx_id`).
- In the project, require it by commit:

  ```toml
  [[require]]
  name = "FixedPoint"
  git = "https://github.com/<owner>/lean4-fixed-point"
  rev = "<full commit hash>"
  ```

  then `lake update FixedPoint` (only that package, so that Mathlib's pin does not move), and commit
  `lakefile.toml` and `lake-manifest.json`.
- During development, before it is published, `path = "../lean4-fixed-point"` replaces `git` and
  `rev`; switch to the pinned commit before the project is pushed.
- Bump the package's Mathlib together with the project's: a project and its packages must agree on
  Mathlib's revision.
- Record the package in the project's README (layout, credits), `REPORT.md` (Section 2, where the
  cited results' proofs are) and `formalization.yaml` (sources and dependencies).

## 7. Palomar

Palomar restricts only the Challenge's imports (`references/palomar.md`, Section 1). The project's
Solution may depend on the package, even after the package is registered as an entry of its own.
Keep the Challenge free of it: definitions that a Challenge statement uses stay in the project's
shared definitions module.
