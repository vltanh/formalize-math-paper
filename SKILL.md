---
name: formalize-math-paper
description: >-
  Formalize a mathematics research paper in Lean 4 with Mathlib, end to end, in any field of
  mathematics: inventory the paper, state every result faithfully, prove the paper's own results
  and then the results it cites, turn an existing Lean draft (often AI-written and never compiled)
  into a project that builds with no sorry or axiom, write a paper-versus-formalization audit
  report, and package the project for the Palomar registry (Challenge/Solution, Comparator,
  formalization.yaml). Use this skill whenever the user wants to formalize, verify, port, repair,
  finish or audit a Lean formalization of a paper, preprint, arXiv link or list of numbered
  theorems; asks to "make this Lean draft compile" or to remove sorries or axioms from one; or
  wants a Lean project made submittable to Palomar, even if they name only one of these steps.
license: Apache-2.0
compatibility: >-
  Any agent that supports Agent Skills (SKILL.md), such as Claude Code, Codex, Gemini CLI,
  Antigravity, GitHub Copilot or Cursor. Needs a shell, git, Python 3 and a Lean 4 toolchain
  (elan); the GitHub CLI and bubblewrap for publishing and Comparator. Parallel sub-agents help
  but are optional.
metadata:
  author: The-Anh Vu-Le
  version: "1.0.0"
  repository: https://github.com/vltanh/formalize-math-paper
---

# Formalizing a mathematics paper in Lean 4

The deliverable is a Lean project, plus documents about it, in which:

- every result the paper proves is proved, following the paper's argument;
- every result the paper cites in its proofs is proved too, in Mathlib or in `External/`;
- the statements say what the paper says, and every deviation is documented;
- `lake build` succeeds with no `sorry`, no `admit`, and no project `axiom`, and every declaration
  depends only on `propext`, `Classical.choice` and `Quot.sound`;
- `REPORT.md` audits the paper against the formalization, and `README.md` summarizes it;
- optionally, the project is packaged and preflighted for Palomar.

The work runs in two stages. In Stage 1, formalize everything the paper itself proves; results it
imports from the literature may be temporary axioms. In Stage 2, discharge those axioms. Around
the two stages come setup, verification, the audit, cleanup and packaging.

## Principles

These explain the rules below. Apply them when a situation is not covered.

- **The paper is the source of truth for statements; Lean is the source of truth for proofs.** A
  statement that drifts from the paper is a wrong formalization, however clean its proof. So
  statements get reviewed against the TeX source before anyone proves them, and never change
  silently afterwards.
- **A formalization nobody compiled is a draft.** Uncompiled Lean written from memory routinely has
  guessed lemma names, wrong signatures and false helper lemmas. Compile whenever a Lean toolchain
  is available. If it is not, or the user forbids it, say plainly that the result is unverified.
- **"Standard", "obvious", "by symmetry", "routine" still need proofs.** Mathlib may have the
  fact; otherwise prove it. Axiomatize only what the paper itself imports from another source.
- **External means provenance, not trust.** A cited result lives in `External/` because of where it
  comes from. It is proved like everything else.
- **Representation choices need bridges.** When Lean's objects differ from the paper's (indices
  from 0 instead of 1, lists instead of indexed families, a bundled Mathlib structure instead of
  an informal object, a concrete model instead of a description "up to isomorphism"), prove the
  lemma that connects them and document the choice. Never assume two representations are
  equivalent.
- **Constants and ranges are mathematics.** Powers, factors, floors, ceilings, strict versus weak
  inequalities, endpoint ranges and truncated subtraction on `ℕ` decide whether a statement is
  true.
- **Report faithfully.** If a step was skipped, a proof fails, or a statement had to change, say
  so. The audit is only useful if it can be trusted.

## Rules

- **Never weaken or change the statement of a paper result to make a proof go through.** If the
  paper's statement is false, stop and tell the user. If they agree, formalize the minimal
  correct version and document it as an error in the report.
- **A false helper lemma** (one you or a draft introduced) gets a concrete counterexample,
  checked in Lean (`decide`, `norm_num` or `#eval`) when that is possible. Then add the minimal
  hypothesis, update its callers, and record the change in the commit message.
- **At the end there is no `sorry`, `admit`, `axiom`, `native_decide` or `implemented_by`.**
  `native_decide` adds the axiom `Lean.ofReduceBool`, which Comparator rejects.
- **Never guess a Mathlib name or signature.** Grep the pinned sources in `.lake/packages/mathlib`,
  or use `#check`, `exact?` and Loogle. Mathlib renames and deprecates often; deprecation
  warnings name the replacement.
- **If compiling is impossible** (no toolchain, or the user forbids it), work in source-only mode.
  Check every name, signature and import path against the pinned Mathlib sources, keep the
  statements-first structure, and label every result as unverified. Whoever compiles it later
  starts at Phase 3.
- **Run one `lake build` at a time per checkout.** Concurrent builds delete each other's `.olean`
  files, and an editor open on the project runs `lake setup-file` builds of its own. If you see
  "object file … does not exist", retry rather than editing around it.
- **Ask before anything outward-facing:** pushing, creating a repository, changing a repository's
  visibility, opening or closing pull requests, deleting branches, submitting to Palomar,
  registering. Permission for one of these is not permission for the others.
- **Authors are people.** AI systems are credited in the README and in the `automation` section of
  `formalization.yaml`, never as authors or maintainers.

## Workflow

| Phase | Goal | Done when |
| --- | --- | --- |
| 0. Configure | record the task, ask the open questions | configuration recorded |
| 1. Inventory | know the paper: results, definitions, constants, citations, suspected typos | working checklist complete |
| 2. Project | a Lean project on current Mathlib, module system, layout by paper section | `lake build` runs |
| 3. Statements | every definition and numbered result stated, proofs `sorry` | statements elaborate and pass a fidelity review |
| 4. Stage 1 | prove everything the paper proves | only cited results remain, as axioms in `External/` |
| 5. Stage 2 | prove the cited results | zero axioms |
| 6. Verify | axiom audit, dependency table, Comparator | `scripts/Audit.lean` passes |
| 7. Cleanup | no warnings, no unused hypotheses, no stale files | build shows only Challenge's `sorry`s |
| 8. Audit | `REPORT.md`, `README.md` | every finding checked against the TeX source |
| 9. Package | CI, Palomar files and checks, publication with permission | preflight reports `status: pass` |

Commit at each milestone, with a message that says what changed and why.

### Phase 0: Configure

Record these, and ask the user only about what you cannot infer:

```text
paper:            arXiv id and version (or DOI); source TeX if available
repository:       new or existing; work on a branch and commit in small coherent steps
starting point:   from scratch, or an existing draft (where?)
Lean / Mathlib:   current Mathlib master unless the user pins a version
compile allowed:  yes (default whenever a toolchain exists)
publishing:       push? create repo? public? (default: ask each time)
target:           Palomar packaging? (default yes when the user mentions Palomar or a registry)
authors:          the human author(s) and maintainer(s), and the license (Apache-2.0 if unspecified)
```

Get the paper's TeX source (on arXiv, the "e-print" download), not only the PDF. Exact
statements, constants and cross-references are much easier to check in TeX.

**Starting from an existing draft.** Import it verbatim as the first commit. Make the commit's
author whoever wrote the draft (for an AI draft, for example `ChatGPT <noreply@openai.com>`),
give it a message that only says what it is ("Uncompiled draft"), and add no co-author trailer.
Do not mix your own edits into that commit. The draft's own notes (checklists that claim
completeness, source maps) describe an unverified state: replace them with `README.md` and
`REPORT.md` at the end. They remain in the history. If the draft came from a pull request in
another repository, offer to close it and delete its branch once the new repository supersedes
it, and do not link to it from the deliverables.

### Phase 1: Inventory

Read the whole paper before writing Lean. Keep a working checklist, outside the deliverables
(a scratch directory or an untracked `notes/`), with:

- definitions and notation, including implicit conventions (logarithm base, what `⊆` means,
  indexing);
- every numbered result, and every displayed equation that a later proof refers to;
- constants, parameter regimes, "without loss of generality" reductions, and where each constant
  is chosen (does `∃ C` come before or after `∀ p`?);
- which result each proof uses: this dependency graph drives the file layout and the parallel
  work in Phase 4;
- each citation, marked as used in a proof or only for context;
- suspected typos, inconsistencies and gaps, with the TeX line. These become the audit's
  E-items, so record them as you go.

### Phase 2: Project

Read `references/lean-project.md` for the details: versions, `lakefile.toml`, the module system
(Palomar requires it in every `.lean` file, scripts included), and the build discipline.

Arrange the files by the mathematical dependency graph, not by size:

```text
PaperName/                     -- the library
  Introduction.lean            -- §1 definitions and statements
  Preliminaries.lean           -- §2
  SectionName/                 -- one directory per major section
    Definitions.lean           -- the section's notation
    Auxiliary.lean             -- lemmas that are not results of the paper
    Lemma34.lean               -- one file per result, or per small group of results
  External/Topic/              -- one directory per cited result
  Main.lean                    -- the main theorem
Challenge.lean                 -- the main results in Mathlib-only vocabulary
Solution.lean                  -- their proofs from the library (may double as the root module)
```

Name declarations after the paper's numbering (`theorem1_2`, `lemma3_4`, `equation_3_1`) so that
readers and scripts can find them. Keep every file under 10,000 lines.

### Phase 3: Statements first

Write every definition, and the statement of every numbered result and reused equation, with
`sorry` proofs, and make the whole project elaborate. Statement errors are the most expensive kind,
and proofs can be parallelized safely only once the statements are fixed.

For an existing draft, `scripts/autosorry.py` replaces each proof that fails to elaborate with
`sorry`. Fix statement errors by hand. Repeat until every file elaborates, then commit ("Make
every statement elaborate").

Then review every statement against the TeX source. Check the quantifier order and where constants
are chosen; strict versus weak inequalities and ranges; casts and truncation (`ℕ` subtraction and
division, `Nat.floor`); indexing from 0 versus 1; "max over z" versus "for every z"; whether
"positive integer" became `ℕ`; and implicit standing assumptions. Prove a bridge lemma for each
representation choice.

Write `Challenge.lean` now: the paper's main results, restated with Mathlib's vocabulary only and
with `sorry` proofs. It is the statement of record. A reader can audit it without reading the
development, and Palomar trusts it because it imports nothing but Mathlib.

### Phase 4: Stage 1, the paper's own results

Prove everything the paper proves, following its proof. A Lean-friendly refactoring is fine if it
is mathematically equivalent; mention it in the report. When a proof step has a typo or a slip,
formalize the intended argument and record the slip as an E-item; the statement does not change.
Results the paper imports from the literature may be stated as axioms in `External/Topic/`, each
with its citation, theorem or equation number, the exact specialization used, and a stable name.

For more than a handful of `sorry`s, split the work by file group, following the dependency
order, among parallel sub-agents if your environment provides them, or work through the groups
one at a time. `references/parallel-repair.md` has the procedure, an agent brief
to copy, and the integration checklist. In particular, compare every declaration's statement with
the pre-repair commit (`scripts/stmt_diff.py`), because agents sometimes change statements
without reporting it.

### Phase 5: Stage 2, cited results

For each cited result:

1. Search Mathlib, at the pinned version, and other public Lean libraries.
2. If it exists, prove that Mathlib's form implies exactly what the paper uses (parameters,
   notation, finite versus infinite, bundled versus unbundled).
3. Otherwise, formalize it under `External/Topic/`, with a `README.md` giving the source, the
   statement and how its Lean forms relate to the paper's use. Proving a different standard form
   is fine if it yields exactly the estimates the paper needs; say so.

End with zero axioms in the project.

### Phase 6: Verify

- `lake build`: no errors, and no `sorry` warnings outside `Challenge.lean`.
- Copy `assets/Audit.lean` to `scripts/Audit.lean`, fill in its lists, and run
  `lake env lean scripts/Audit.lean`. It checks the axioms of every declaration of the library,
  of the paper's results and of the Challenge theorems, and lists which cited results each paper
  result uses (the dependency table for the report). Under the module system it needs
  `import all` for every module; the template explains why.
- Run `lake comparator` (needs bubblewrap; see `references/palomar.md`).
- A green build proves only what the statements say, so ask of the formalization:
  - Does a helper lemma hide half a proof, through a hypothesis that assumes what should be shown?
  - Is a hypothesis stronger than the paper's?
  - Could a statement be vacuous: contradictory hypotheses, an empty range, a definition that is
    never satisfied?
  - Is each result in `External/` really cited by the paper, rather than proved in it?
  - Does each library theorem used for a cited result imply exactly the paper's form?
  - Are sums, counts and unions taken over exactly the paper's index sets?
  - Are the constants exact?

### Phase 7: Cleanup

Read `references/cleanup.md`. In short: remove unused hypotheses with `scripts/strip_unused.py`,
over several rounds because each removal can leave others unused. Fix the remaining linter
warnings, and rename files or namespaces whose names mislead (for example, helper files called
`External`). Delete stale notes. An unused hypothesis of a paper result is one that the paper's
statement does not need: remove it, which makes the Lean statement more general than the
paper's, and record it for the audit. Challenge statements stay exactly the paper's.

### Phase 8: Audit report and documentation

Read `references/audit-report.md` for the structure of `REPORT.md` and `README.md` and how to
check findings. Start from what the earlier phases recorded: the slips and gaps noted while
reading and proving, and the hypotheses that the cleanup removed. Two things users care about:

- The report analyzes the paper and the current formalization. It is not a history of the
  repair, and it does not point to superseded drafts or pull requests.
- Every claim about the paper is checked against the TeX source, and every arithmetic claim is
  recomputed. A wrong error report costs more credibility than a missed typo.

Keep links from the documents to the code current with `scripts/linkify_docs.py` (it reads the
`.ilean` files, so run it after `lake build`), and check Markdown tables with
`scripts/check_md_tables.py`: in GitHub's Markdown, a `|` inside a table cell splits the cell even
inside backticks.

### Phase 9: Package and publish

Read `references/palomar.md`. It covers the required files, `formalization.yaml`, Palomar's own
validation scripts, CI (`assets/lean_action_ci.yml`), the preflight workflow
(`assets/palomar_preflight.yml`), and the submission protocol. Push, publish and submit only with
the user's explicit go-ahead for each step. Submit only a commit whose preflight report says
`status: pass`, and never register on the user's behalf.

## Bundled tools

Run the scripts from the project root, as `python3 <skill-dir>/scripts/<name> …`. Copy the ones
that CI runs into the project's `scripts/` directory.

| Tool | Use |
| --- | --- |
| `scripts/check_file.py FILE [--autosorry]` | check one file with the lakefile's options; with `--autosorry`, replace failing proofs by `sorry` until the file elaborates |
| `scripts/autosorry.py FILE LOG` | the replacement step on its own, given Lean's output |
| `scripts/to_module.py FILE…` | convert files to the module system |
| `scripts/stmt_diff.py REV [PATH…]` | list the declarations whose statements or definitions changed since `REV` |
| `scripts/strip_unused.py LOG [--dry-run]` | delete the binders that the unused-variables linter reports |
| `scripts/linkify_docs.py [--check]` | link the Lean names in the documents to their lines; copy it into the project and configure its first block |
| `scripts/check_md_tables.py FILE… [--fix]` | find, or fix, Markdown table rows broken by a `\|` inside a cell; copy it into the project |
| `assets/Audit.lean` | the axiom and dependency audit; copy it to `scripts/Audit.lean` and fill in its lists |
| `assets/lean_action_ci.yml` | CI: build, audit, links, tables |
| `assets/palomar_preflight.yml` | Palomar's mechanical preflight, run on demand |

## Status reports

When reporting progress, use this shape, filling in only what applies:

```text
repository / branch / head:
phase:
build:            passes / fails (first error)
sorry / axiom:    counts (excluding Challenge.lean)
statements:       changes to paper results (should be none), helper lemmas found false
stage 1 / 2:      remaining internal / cited results
audit:            findings so far (E-items)
packaging:        Comparator, Palomar checks, preflight
needs from user:  decisions or permissions
```

## Completion gates

- **Statements:** every numbered result stated; fidelity review done; representation bridges
  proved; Challenge written.
- **Stage 1:** every internal result proved; cited results isolated in `External/` with citations.
- **Stage 2:** every cited result proved or derived from Mathlib; zero project axioms.
- **Verification:** clean build; `scripts/Audit.lean` passes for every declaration; Comparator
  accepts the solution.
- **Cleanup:** the build prints only Challenge's `sorry` warnings; unused hypotheses removed, and
  those of paper results recorded; misleading names fixed; stale draft notes deleted.
- **Documentation:** `REPORT.md` and `README.md` written, links current, tables valid, findings
  checked against the source.
- **Packaging (if wanted):** CI green; Palomar's metadata and source checks pass; preflight
  `status: pass` on the exact commit to submit; the user decides about submission and
  registration.
