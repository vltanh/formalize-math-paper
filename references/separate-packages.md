# Packages of their own

Research papers use theory that no Lean library has yet, and the project builds it (SKILL.md,
Rules, "Mathematics that Lean lacks"). A theory that others could use goes in a Lake package of its
own, in its own repository, required by the project at a pinned commit: it outlasts the project,
others can import it, and it can move to Mathlib later. A lemma, or a short development that only
fills a gap of this paper, stays in the project: general mathematics in `Basic/`, cited results in
`External/` (SKILL.md, Phase 2).

## 1. The test

Put the missing mathematics in a package of its own when all of these hold:

- Missing. Neither Mathlib nor another maintained public Lean library has it, and no Mathlib
  pull request for it is close to merging.
- A theory. It is more than one quick contribution to Mathlib: definitions and the results around
  them that the proof builds on, as a rough guide several hundred lines or more. A theorem known
  by name, with the theory under it, qualifies (Kakutani's fixed-point theorem, the
  Kahane–Khintchine inequality, the `L^p` boundedness of the Hilbert transform); one long lemma
  that only this paper needs does not.
- General. Its statements say nothing about the paper's objects, and it imports only Mathlib
  and other such packages.
- Reusable. Someone outside this project could plausibly import it.

Otherwise it stays in `Basic/` or `External/`, and small general lemmas are offered to Mathlib, the
long-term home of general mathematics. Decide during the inventory (Phase 1), so that the code is
written in the package from the start rather than moved there later. Build the package by default
and say so in the next status report, with the plan and its estimate. The user decides its name,
its visibility and when to publish it, and may prefer to keep it in the project. Building it
locally needs no permission; creating and pushing its repository does (Rules).

State the package's results in their general form, as a library would, when the general proof is
not much harder than the case the paper needs. Otherwise prove the case needed, say so in the
statement's docstring, and list the general form in the package's README as a planned extension.

## 2. One package per area

Name a package for its area, not for one theorem (`lean4-<area>`, not `lean4-<theorem>`), so that
related results can join it later instead of starting more repositories. Inside it, give each
theorem its own directory (`<Area>/<Theorem>/`). Before proposing a new package, check whether an
existing one is the right home.

## 3. The package stands alone

Others will import the package without knowing the project, so it reads as a library of its own.

- It is a Lake package with the project's `lean-toolchain` and Mathlib release, the module system,
  Mathlib's style, its own README (what it proves, with the exact statements; the method and its
  references; how to depend on it; credits: its maintainers, and the AI systems that wrote it, as
  the Rules require), licence, CI and axiom audit. The README is short, as the project's is
  (`audit-report.md`, Section 3); long explanations go in a `docs/` file it links. It states only
  what is true of the package: where a fact is not settled yet (a commit hash, the exact form of a
  statement, a file name), it leaves a marked placeholder rather than a plausible guess. While
  proofs are still open, the audit may list the `sorry`s instead of failing on them; switch that off
  before publishing. Its library globs are `<Area>.*`, since Lake's `.+` would skip the root file.
- It carries no provenance. It says what it proves and on which mathematical sources, not what it
  was written for, who asked for it, or how it was made. Code split out of the project needs no
  credit, and no README, docstring, comment, name or commit message of the package mentions the
  project (the paper, its objects or authors, the project's repository or paths). Code taken from
  someone else's work is the exception: credit it, and keep its licence notice
  (`palomar.md`, Section 1).
- Tell everyone who writes in the package, agents included, that it stands alone, and before
  publishing search its files and commit messages for the paper's title and authors, the project's
  repository, and phrases such as "for the formalization of" or "at the request of".

## 4. Depending on it

- The project requires it by `path = "../lean4-<area>"` while it is developed, and by its published
  commit (`git = …`, `rev = "<full commit hash>"`) once it is published; run `lake update <Area>`
  alone, so that Mathlib's pin does not move. A path outside the repository builds nowhere else, so
  the project cannot be pushed until the package is published. A project and its packages share
  one Mathlib revision and are upgraded together.
- To avoid rebuilding Mathlib for the package, hard-link the project's `.lake/packages` and copy the
  Mathlib entries of its manifest. The project's builds also build the package through the path
  dependency, so agents working in both at once check files without building
  (`scripts/check_file.py`) and build only when their files are done.
- A cited result keeps its place in the project: `External/` states it in its source's terms and
  proves it from the package. The route check and the audit treat it like any other cited result.
- The project's README, `REPORT.md` (Section 2) and `formalization.yaml` say where it uses the
  package; the dependency runs one way.
- Palomar restricts only the Challenge's imports (`references/palomar.md`, Section 1): the Solution
  may depend on the package, even when the package is registered as an entry of its own.
