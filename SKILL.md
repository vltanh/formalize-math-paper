---
name: formalize-math-paper
description: >-
  Formalize a mathematics research paper in Lean 4 with Mathlib, end to end, in any area of
  mathematics: inventory the paper, state each result faithfully, prove the paper's own results and
  then the results it cites, make an existing Lean draft (often AI-written and never compiled) build
  with no sorry or axiom, audit the paper against the formalization in a report, and package the
  project for the Palomar registry (Challenge/Solution, Comparator, formalization.yaml). Use this
  skill whenever the user wants to formalize, verify, port, repair, finish or audit a Lean
  formalization of a paper, preprint, arXiv link or list of numbered theorems; asks to "make this
  Lean draft compile" or to remove its sorries or axioms; or wants a Lean project ready to submit to
  Palomar, even if they name only one of these steps.
license: Apache-2.0
compatibility: >-
  Any agent that supports Agent Skills (SKILL.md), such as Claude Code, Codex, Gemini CLI,
  Antigravity, GitHub Copilot or Cursor. Needs a shell, git, Python 3 and a Lean 4 toolchain
  (elan), plus the GitHub CLI and bubblewrap to publish and to run Comparator. Parallel sub-agents
  help but are optional.
metadata:
  author: The-Anh Vu-Le
  version: "2.1.0"
  repository: https://github.com/vltanh/formalize-math-paper
---

# Formalizing a mathematics paper in Lean 4

You deliver a Lean project, with documents about it, in which:

- every result the paper proves is proved by the paper's own argument. A proof departs from
  the paper's only when it must, and every departure is reported (Rules, "Faithful proofs");
- every result the paper cites in its proofs is proved too: in Mathlib, in another public
  library, or in `External/`. A cited result may need mathematics that no Lean library has yet and
  that the project cannot reasonably build. Such a result becomes a named hypothesis of every
  statement that uses it, and the formalization then says plainly that it is conditional;
- the statements say what the paper says, and every deviation is documented;
- `lake build` succeeds with no `sorry` (except in the statements of `Challenge.lean`, by design),
  no `admit` and no project `axiom`. Every declaration of the library depends only on `propext`,
  `Classical.choice` and `Quot.sound`;
- `REPORT.md` audits the paper against the formalization. It ends with what comes next: how the
  subject has developed since the paper, how its results could be extended, generalized or
  strengthened, and how its proofs could be simpler. `README.md` summarizes the formalization, and
  `CREDITS.md` says how it was made: the procedure, the agents and models, and the time and effort
  (the run log);
- the project is packaged for Palomar and, with the user's permission, published and run through
  Palomar's preflight.

The work has two stages. In Stage 1, formalize everything the paper itself proves. Results it takes
from the literature may be temporary axioms. In Stage 2, remove those axioms: prove them, or
turn the ones out of reach into stated hypotheses. Setup comes before the two stages, and
verification, cleanup, the audit and packaging come after.

## Principles

These explain the rules below. Use them when no rule covers a situation.

- **The paper is the source of truth for statements and arguments; Lean judges correctness.** A
  statement that differs from the paper's is a wrong formalization, however clean its proof. So is
  a proof that reaches the paper's statement by another argument: the formalization checks the
  paper's proofs, not only its claims. Review statements against the TeX source before anyone
  proves them. Compare proofs with the paper's proofs once they are written. Never change either
  silently.
- **A formalization nobody has compiled is a draft.** Lean written from memory and never
  compiled often has guessed lemma names, wrong signatures and false helper lemmas. Compile
  whenever a Lean toolchain is available. If none is, or the user forbids compiling, say plainly
  that the result is unverified.
- **"Standard", "obvious", "by symmetry", "routine" still need proofs.** Mathlib may have the fact;
  if not, prove it. Only what the paper itself takes from another source may become an axiom.
- **External means where a result comes from, not that it is trusted.** A cited result lives in
  `External/` because of its source. It is proved like everything else.
- **An assumption is an assumption, whatever its form.** A cited result that is not proved is
  assumed, whether it is written as an axiom, a hypothesis or a field of a structure. Axioms are not
  allowed. Hypotheses are allowed when a reader of the statement can see each one, under the name
  of the result it assumes. A structure that mixes data with assumed theorems hides what a result
  depends on. So does a parameter whose type looks like data but holds a theorem.
- **Data comes with its defining property.** When a statement takes an object of the paper as a
  parameter instead of constructing it, it must also require the property that defines the object.
  Otherwise the theorem is about every object that satisfies the other hypotheses, which is a
  different statement.
- **Representation choices need bridges.** Lean's objects may differ from the paper's: indices
  from 0 instead of 1, lists instead of indexed families, a bundled Mathlib structure instead of an
  informal object, a concrete model instead of a description "up to isomorphism". When they do,
  prove a lemma that connects the two, and document the choice. Never assume two representations
  are equivalent.
- **Constants and ranges are part of the mathematics.** Powers, factors, floors, ceilings, strict
  versus weak inequalities, the endpoints of ranges and truncated subtraction on `ℕ` decide whether
  a statement is true.
- **Report honestly.** If a step was skipped, a proof fails, a statement had to change, or a proof
  had to depart from the paper's, say so and give the reason. The audit is useful only if it can be
  trusted.
- **A gap in a proof is not a false statement.** When the paper's proof uses a fact that its
  hypotheses do not give, the statement may still be true. Look for a correct argument before you
  conclude anything about the statement.
- **Measure the work.** Readers and registries ask how a formalization was made. The answer is
  cheap to record as you go, and hard to reconstruct afterwards.

## Rules

- **Never weaken or change the statement of a paper result to make a proof work.** If the paper's
  statement is false, stop work on it and tell the user at once, with the counterexample. Other
  work can continue meanwhile. If the user agrees, formalize the closest correct version and record
  it as an error in the report. Obvious misprints are the one exception (below).
- **Never add a hypothesis to a paper result because its proof seems to need it.** Adding one
  weakens the result. Add one only when the statement itself has a counterexample, not because a
  step of the proof fails, and then follow the previous rule. Otherwise prove the statement as
  printed, by a corrected argument, and record the gap in the proof as an E-item. If you find
  neither a proof nor a counterexample, tell the user what is missing. They decide whether to keep
  working or to formalize a weaker statement, documented as a deviation.
- **Faithful proofs.** Prove every result by the paper's proof: the same intermediate claims, the
  same constructions and case splits, and the same earlier results where the paper cites them. The
  results that the paper's proof cites form its *route*. The formal proof must have the same route,
  and the route check (Phase 6) verifies this. Only the mechanics may differ: tactics, the Mathlib
  lemma that closes a routine step, the order of independent steps, and helper lemmas that package
  a step of the paper. If Mathlib happens to prove a numbered result, prove it by the paper's
  argument anyway, unless the paper itself treats it as known (it cites it, or calls it standard).
- **Depart from the paper's proof only when you must**, that is, for one of these reasons and no
  other:
  1. the paper's argument is wrong at that step, or has a gap there, and cannot be repaired along
     its own lines (the step is also an E-item);
  2. the step needs mathematics that Lean lacks and that the project cannot reasonably build (as
     for cited results out of reach, below), and another argument avoids it;
  3. the step has no meaning in a representation that the formalization must use (Principles), so
     a faithful translation of it is a different argument.

  A shorter, more elegant, more general or more automatic proof is not a reason. Neither is a proof
  that is easier to formalize or faster to build. A simpler argument that you find is still worth
  keeping: record it, with a sketch, for the report's "What's next" section (Phase 8), and prove
  the result by the paper's argument. Depart as little as the reason requires: repair
  the step, not the proof. If a departure would replace the whole argument of a numbered result,
  not just one step, propose it to the user first, with the reason. Other work continues meanwhile.
- **Report every departure, always.** For each one, record what the paper does, what the
  formalization does instead, and which reason forces the change. Record it in the declaration's
  docstring ("Departure from the paper: …"), in the report's table of departures, in
  `formalization.yaml` (`fidelity.divergences`), in any companion text, in the route check's file
  of recorded differences when the route changes, and in the next status report. A departure
  missing from any of these is a defect: find and fix it as you would a statement that was changed
  silently.
- **Cited results out of reach.** A cited result may need mathematics that no Lean library has. If
  building that mathematics in the project is a moderate effort, build it. Otherwise the default is
  a conditional formalization: the result becomes a named hypothesis of every statement whose proof
  uses it. Apply the default without asking, and report it in the next status report. Ask the user
  only when building the missing mathematics would be a large but feasible effort: whether to spend
  that effort is their decision. Meanwhile, continue the other work under the default. If they
  choose to build it, plan the work in layers. Each layer replaces some hypotheses with
  constructions and proofs from more basic ones, and ends in a state that can be released. These
  hypotheses are the only ones that may be added to a paper result without a counterexample. Never
  present a conditional formalization as complete: its README, `formalization.yaml` and report say
  that it is conditional and list what it assumes.
- **Slips in statements.** If a statement is false only because of an obvious misprint (a wrong
  index, a swapped name, a missing `- 1`), and only one reading can be intended, formalize that
  reading at once, in the library and in the Challenge. List each such correction in the report
  and in the next status report to the user. When more than one fix is possible, treat the
  statement as false.
- **A false helper lemma** (one you or a draft introduced) needs a concrete counterexample,
  checked in Lean (`decide`, `norm_num` or `#eval`) when possible. Then add the minimal hypothesis,
  update its callers, and record the change in the commit message.
- **At the end there is no `sorry` (outside `Challenge.lean`), `admit`, `axiom`, `native_decide`
  or `implemented_by`.** `native_decide` adds an axiom, which Comparator rejects.
- **Never guess a Mathlib name or signature.** Grep the pinned sources in `.lake/packages/mathlib`,
  or use `#check`, `exact?` and Loogle. Mathlib often renames and deprecates declarations, and
  deprecation warnings name the replacement.
- **If you cannot compile** (no toolchain, or the user forbids it), write the Lean without
  compiling it. Check every name, signature and import path against the pinned Mathlib sources,
  keep the statements-first order, and label every result as unverified. Whoever compiles the
  project later starts at Phase 3.
- **Run one `lake build` at a time per checkout.** Builds that run at the same time delete each
  other's `.olean` files, and an editor open on the project runs its own `lake setup-file` builds.
  If you see "object file … does not exist", retry instead of editing around it.
- **Ask before any action that others can see:** pushing, creating a repository, changing a
  repository's visibility, opening or closing pull requests, deleting branches, running Palomar's
  preflight, submitting to Palomar, registering. Permission for one of these is not permission for
  the others.
- **Authors are people.** Credit AI systems in the README, in `CREDITS.md` and in the `automation`
  section of `formalization.yaml`, never as authors or maintainers.
- **Keep a run log** from the start (see "Run log" below). Report it in `CREDITS.md`, in
  `formalization.yaml` and in status reports.

## Workflow

| Phase | Goal | Done when |
| --- | --- | --- |
| 0. Configure | record the task, ask the open questions | configuration recorded |
| 1. Inventory | know the paper: its results, definitions, constants, citations and where their proofs can come from, suspected typos | working checklist complete |
| 2. Project | a Lean project on a Mathlib release, with the module system, laid out by paper section | `lake build` runs |
| 3. Statements | every definition and numbered result stated, with `sorry` proofs; the Challenge | statements elaborate and pass an independent review against the paper; baseline committed |
| 4. Stage 1 | prove everything the paper proves, by the paper's proofs | only cited results remain, as axioms in `External/`; every departure reported |
| 5. Stage 2 | prove the cited results | zero axioms; every result still assumed is a named hypothesis |
| 6. Verify | axiom audit, dependency table, route check, Solution and Comparator | `scripts/Audit.lean` and the route check pass; proofs compared with the paper's; Comparator accepts |
| 7. Cleanup | no warnings, no unused hypotheses, no misleading names, routes unchanged | the build shows only the Challenge's `sorry`s; the route check still passes |
| 8. Audit | `REPORT.md`, `README.md`, `CREDITS.md` | every finding checked against the TeX source |
| 9. Package | CI, Palomar files and checks; publishing and preflight, with permission | Palomar's local checks pass; after publishing, the preflight reports `status: pass` |

Commit at each milestone, with a message that says what changed and why.

### Phase 0: Configure

Record these. Ask the user only about what you cannot work out yourself:

```text
paper:            arXiv id and version (or DOI); source TeX if available; later versions (a newer
                  arXiv version, the published version, errata), found by searching now
repository:       new or existing; work on a branch and commit in small, coherent steps
starting point:   from scratch, or an existing draft (where?)
Lean / Mathlib:   the newest Lean release or release candidate (at least Palomar's minimum), and
                  Mathlib's release tag for it, unless the user pins a version or a library the
                  project needs requires a specific Mathlib commit
libraries:        the public libraries beyond Mathlib that prove results the paper cites
                  (references/palomar.md, Section 1, says which may appear in statements)
out of reach:     cited results that no library supports and the project cannot build, and how
                  each is handled (Rules)
compile allowed:  yes (the default whenever a toolchain exists)
publishing:       push? create a repository? make it public? (default: ask each time)
target:           Palomar packaging (default yes; skip it only if the user declines)
authors:          the human author(s) and maintainer(s), and the license (Apache-2.0 if not given)
run log:          the start time with its time zone, the agent, model and procedure (this skill, with
                  its repository and version), recorded now
earlier work:     earlier formalizations of the same paper or result, and of the results it cites,
                  found by searching now
```

Get the paper's TeX source (on arXiv, the "TeX Source" link), not just the PDF. Exact statements,
constants and cross-references are much easier to check in TeX.

Before starting, search for later versions of the paper (a newer arXiv version, the published
version, errata) and for earlier formalizations of the paper or of its main result (GitHub, the Lean
Zulip, the Palomar registry, collections of formal statements, and the roadmaps of the large
libraries). Tell the user what you find, or that you could not search without network access. If the
version you were given is not the latest, say what the later ones change, and ask which version to
formalize. An earlier formalization changes what a new one should add. The README and
`formalization.yaml` must cite it, and Palomar's review asks whether a submission duplicates
existing work.

**Starting from an existing draft.** Import it unchanged as the first commit. Make the commit's
author whoever wrote the draft (for an AI draft, for example, `ChatGPT <noreply@openai.com>`).
Give the commit a message that only says what it is ("Uncompiled draft"), and add no co-author
trailer. Do not mix your own edits into that commit. The draft's own notes (checklists that claim
it is complete, source maps) describe a state that nobody verified: replace them with `README.md`
and `REPORT.md` at the end. They remain in the history. If the draft came from a pull request in
another repository, offer to close the pull request and delete its branch once the new repository
replaces it. Do not link to it from the deliverables.

### Phase 1: Inventory

Read the whole paper before you write any Lean. Keep a working checklist outside the deliverables
(in a scratch directory or an untracked `notes/`), with:

- definitions and notation, including implicit conventions (the base of logarithms, what `⊆`
  means, indexing);
- every numbered result, and every displayed equation that a later proof refers to;
- constants, conditions on the parameters (ranges, "n large enough"), "without loss of generality"
  reductions, and where each constant is chosen (does `∃ C` come before or after `∀ p`?);
- which results each proof uses. This dependency graph decides the file layout and the parallel
  work in Phase 4, and it is the route that each formal proof must follow. Extract it from the TeX
  source with `python3 <skill-dir>/scripts/route_check.py extract main.tex > docs/paper_routes.tsv`,
  and commit the file as extracted. Compare it with your own reading: a proof may cite a result
  only in passing, which the route check's file of recorded differences says later;
- each citation, marked as used in a proof or only for context. For each one used in a proof, note
  where its proof can come from: Mathlib, another public library, the project itself, or nowhere
  yet, because the mathematics it needs is missing from Lean. Survey the libraries before you
  decide, and decide now how to handle the last kind (Rules), because it sets the scope;
- suspected typos, inconsistencies and gaps, with the TeX line, and the corrections that errata or
  later versions make (Phase 0). These become the audit's E-items, so record them as you go. Settle
  a correction that changes a statement before the baseline (Phase 3, Rules);
- the paper's open questions, conjectures and remarks on what its method could give, and the
  hypotheses it says it needs only for its method. They are the starting point of the report's
  "What's next" section (Phase 8).

### Phase 2: Project

Read `references/lean-project.md` for the details: versions, `lakefile.toml` (with placeholder
`Challenge.lean` and `Solution.lean` files from the start), the module system (Palomar requires it
in every `.lean` file, scripts included), and the rules for building.

Arrange the files by the mathematical dependency graph, not by size. Each module imports only what
it uses. That way, an edit rebuilds only what depends on it, and parallel work does not stall.

```text
PaperName/                     -- the library
  Introduction.lean            -- §1 definitions and statements
  Preliminaries.lean           -- §2
  SectionName/                 -- one directory per major section
    Definitions.lean           -- the section's notation
    Auxiliary.lean             -- lemmas that are not results of the paper
    Lemma34.lean               -- one file per result, or per small group of results
  External/Topic/              -- one directory per cited result, with a README.md, from the start
  Main.lean                    -- the main theorem
Challenge.lean                 -- the main results, in the vocabulary of Mathlib
Solution.lean                  -- their proofs from the library (may double as the root module)
```

Name declarations after the paper's numbering (`theorem1_2`, `lemma3_4`, `equation3_1`), so that
readers and scripts can find them. Begin the docstring of every numbered result with its number and
its TeX label in backticks (``**Theorem 1.2** (`thm:main`).``). The route check uses these labels
to find the paper's results in the Lean code. Keep every file under 10,000 lines.

### Phase 3: Statements first

Write every definition, and the statement of every numbered result and reused equation, with
`sorry` proofs. Make the whole project elaborate. Errors in statements are the most expensive kind,
and proofs can safely be done in parallel only once the statements are fixed.

For an existing draft, `scripts/autosorry.py` replaces each proof that fails to elaborate with
`sorry`. Fix errors in statements by hand. Repeat until every file elaborates, then commit ("Make
every statement elaborate").

Write `Challenge.lean`: the paper's main results, and only those, restated with `sorry` proofs in
Mathlib's vocabulary. (Palomar also allows Tau Ceti's, but then marks the entry as having qualified
statement dependencies; see `references/palomar.md`, Sections 1 and 2.) The Challenge is the
statement of record. A reader can check it without reading the rest of the project, and Palomar
trusts it because it imports nothing beyond the libraries that Palomar allows. Intermediate results
stay proved in the library, linked from the README. Plan the Challenge's size from the start:
Palomar allows at most 1,000 lines and prefers 300, and the definitions the statements need count
too. When the Challenge defines an object that a reader cannot recognize at a glance, add a
compared theorem that ties it to something known about it, such as a known numerical value.
Readers and Palomar's review can then tell that the definition is the intended one. A conditional
result shows every assumed result in the signature of each theorem that uses it (Phase 5).

Then review every statement, including the Challenge's, against the TeX source. Check the order of
quantifiers and where constants are chosen; strict versus weak inequalities, and ranges; casts and
truncation (`ℕ` subtraction and division, `Nat.floor`); indexing from 0 versus 1; "max over z"
versus "for every z"; whether "positive integer" became `ℕ`; the types Lean inferred where the
statement does not give them; implicit standing assumptions; and whether every hypothesis of a
statement is either the paper's or a declared assumption. Prove a bridge lemma for each
representation choice.

Have the statements and the Challenge reviewed against the TeX source by someone other than their
writer: a separate agent if your environment has them, otherwise a separate pass of your own. Then
commit. This commit is the **baseline**. Later changes to statements are measured against it, and
after it a statement changes only by a documented decision.

### Phase 4: Stage 1, the paper's own results

Prove everything the paper proves by the paper's proof (Rules, "Faithful proofs"). The Lean
mechanics may differ from the paper's text; the argument may not. When a proof step has a typo or a
slip, formalize the intended argument and record the slip as an E-item. When a step fails, repair
that step, keep the rest of the paper's argument, and report the departure. In both cases the
statement does not change.
Results the paper takes from the literature may be stated as axioms in `External/Topic/`. Give
each one its citation, its theorem or equation number, the exact special case used, and a stable
name. Put cited results there from the start, including facts the paper uses only in a
special case: moving files into `External/` later means renaming modules and rewriting imports.

When a result needs an argument that the paper does not give (an unproved theorem, a gap in a
proof, a numerical claim), work out the mathematics before you assign it. Reduce it to steps that
can be checked, test the steps numerically, and give the agent the plan and the numbers.
`references/numerics.md` covers rigorous numerics in Lean.

For more than a handful of `sorry`s, split the work into groups of files, in dependency order. Give
the groups to parallel sub-agents if your environment has them, or work through the groups one
at a time.
`references/parallel-repair.md` has the procedure, an agent brief to copy, and the checklist for
integrating the results. Give each agent the TeX of the paper's proofs of its results, to follow.
Compare every declaration's statement with the baseline commit (`scripts/stmt_diff.py`), and every
route with the paper's (the route check, Phase 6). Agents sometimes change statements, or argue
differently from the paper, without reporting it. Add the simpler arguments that agents report to
the checklist, with those you notice yourself.

### Phase 5: Stage 2, cited results

For each cited result:

1. Search Mathlib, at the pinned version, and the other public Lean libraries. A library used only
   in proofs may be any pinned public repository. A library whose definitions the Challenge needs
   must be one that Palomar allows in statements (`references/palomar.md`, Section 1). Depending
   on a library can require a specific Mathlib commit: settle that before you build on it.
2. If the result is there, prove that the library's form implies exactly what the paper uses
   (parameters, notation, finite versus infinite, bundled versus unbundled).
3. Otherwise, formalize it under `External/Topic/`, with a `README.md` that gives the source, the
   statement, and how its Lean forms relate to the way the paper uses it. Proving a different
   standard form is fine if it gives exactly the estimates the paper needs; say so.
4. If neither is feasible, because the mathematics it needs is missing from Lean and beyond the
   project, follow the rule on cited results out of reach. By default, define the result in
   `External/Topic/` as a proposition named after its source, with no proof. Make it a hypothesis
   of every statement whose proof uses it, including the Challenge's. Several such hypotheses may
   be bundled in a class of hypotheses, named for what it is. The class takes the data as
   parameters, and is written in the signature of each theorem that needs it. The topic's
   `README.md` says what Lean lacks. If the user chose to build the missing mathematics, write down
   the layers before you start the first, and keep the end state of every layer releasable.

At the end, the project has no axioms, and every cited result is either proved or, when out of
reach, a declared hypothesis.

### Phase 6: Verify

- `lake build`: no errors, and no `sorry` warnings outside `Challenge.lean`.
- Copy `assets/Audit.lean` to `scripts/Audit.lean`, fill in its lists, and run
  `lake env lean scripts/Audit.lean`. It checks the axioms of every declaration of the library, of
  the paper's results and of the Challenge theorems. It also lists which cited results each paper
  result uses (the dependency table for the report). Under the module system it needs `import all`
  for every module; the template explains why.
- Run the route check. The audit writes the routes of the formal proofs to `.lake/route_deps.tsv`,
  and `python3 scripts/route_check.py check docs/paper_routes.tsv --accept
  docs/route_differences.tsv` compares them with the routes of the paper's proofs. It reports any
  result whose proof does not use a result that the paper's proof cites, or uses one that the
  paper's argument never reaches. Settle every difference. Either change the Lean proof to follow
  the paper, or, if the difference is a necessary departure (Rules) or a use that the paper leaves
  implicit, record it with its reason in `docs/route_differences.tsv`. Report a departure
  everywhere the rules say. The check sees which results a proof uses, not how it argues. So also
  have someone other than the provers compare the formal proofs with the paper's, against the TeX:
  at least every proof that is long, that was written in parallel, or that changed since the last
  comparison.
- Complete `Solution.lean`, which restates each Challenge theorem word for word and proves it from
  the library, and write `comparator.json` (`references/palomar.md`, Sections 2 and 3). Then run
  `lake comparator` (it needs bubblewrap; see `references/palomar.md`, Section 5).
- A passing build proves only what the statements say. So ask of the formalization:
  - Does a helper lemma hide half a proof, through a hypothesis that assumes what should be shown?
  - Is a hypothesis stronger than the paper's?
  - Could a statement be vacuous: hypotheses that contradict each other, an empty range, a
    definition that nothing satisfies? Construct an instance of each structure or class of
    hypotheses that a statement takes, or say in the report why that is not yet possible.
  - Does a parameter hide an assumption? For every structure, class or subtype that a Challenge
    theorem takes, list its propositional content, recursively, and classify each item: a
    hypothesis of the paper, a law that defines the object, a fact proved in the project, or an
    assumed result. Every assumed result must be a declared hypothesis, named after its source and
    listed in the report.
  - Is every object that a statement takes as a parameter tied to its defining property?
  - Is each result in `External/` really cited by the paper, rather than proved in it?
  - Does each library theorem used for a cited result imply exactly the paper's form?
  - Does each proof follow the paper's argument, and is every departure necessary and reported?
  - Are sums, counts and unions taken over exactly the paper's index sets?
  - Are the constants exact?

### Phase 7: Cleanup

Read `references/cleanup.md`. In short: remove unused hypotheses with `scripts/strip_unused.py`,
then the arguments that call sites still pass for them with `scripts/strip_call_args.py`. Work in
rounds, each starting from a commit, because each removal can leave other hypotheses unused. Fix
the remaining linter warnings, and rename files or namespaces whose names mislead (for example,
helper files called `External`). An unused hypothesis of a paper result is one that the paper's
statement does not need. Remove it, which makes the Lean statement more general than the paper's,
and record it for the audit. Challenge statements keep the paper's hypotheses. An assumed result
that no proof uses is not a hypothesis of the paper: remove it everywhere, including the
Challenge.

Cleanup changes how proofs are written, never which argument they make. Merging duplicate helpers,
shortening proofs and splitting files can change a proof's route without changing any statement.
For example, a step that the paper justifies by a numbered result ends up using the lemma
underneath that result, or a shorter argument replaces the paper's. Of two copies of a fact, keep
the one that follows the paper's citations, and rerun the route check after every round. A new
difference after a cleanup is a regression to undo, not a departure to record.

### Phase 8: Audit report and documentation

Read `references/audit-report.md` for the structure of `REPORT.md` and `README.md` and for how to
check findings, and `references/credits.md` for the structure of `CREDITS.md`. Start from what the
earlier phases recorded: the slips and gaps noted while reading and proving, and the hypotheses that
the cleanup removed. Have every finding verified against the TeX source by someone other than the
one who recorded it (a separate agent if available). In practice this overturns some of the
inventory's own claims, and can show that a statement was changed without need. When it does,
restore the paper's statement, rerun the Phase 6 checks, and update the Challenge and the report to
match. A conditional formalization says so in the README's first paragraph, and the report lists
every assumed result. Once `README.md` and `REPORT.md` exist, delete a draft's own notes (Phase 0).
Users care about three things:

- The report analyzes the paper and the current formalization. It is not a history of the repair,
  and it does not point to old drafts or pull requests.
- The report lists every departure from the paper's proofs, with its reason, and so does the
  README's summary. If every proof follows the paper's, both say so.
- Every claim about the paper is checked against the TeX source, and every arithmetic claim is
  recomputed. A wrong error report costs more trust than a missed typo.

End the report with its "What's next" section: how the subject has developed since the paper, how
its results could be extended, generalized or strengthened, and how its proofs could be simpler,
from the simpler arguments recorded during the work. Write it from a dated search for
the work that followed the paper, including versions of the paper newer than the one formalized,
and have it checked like the findings (`references/audit-report.md`, Sections 1 and 2). Without
network access, say so, and write it from the paper and the audit. Later work that corrects the
paper is also a finding: record it as one, and tell the user at once.

Keep the documents' links to the code up to date with `scripts/linkify_docs.py`. It reads the
`.ilean` files, so run it after `lake build`. Check Markdown tables with
`scripts/check_md_tables.py`: in GitHub's Markdown, a `|` inside a table cell splits the cell, even
inside backticks.

### Phase 9: Package and publish

Package for Palomar unless the user declined in Phase 0. Read `references/palomar.md`. It covers
the required files, `formalization.yaml`, Palomar's own validation scripts, CI
(`assets/lean_action_ci.yml`), the preflight workflow (`assets/palomar_preflight.yml`), and how to
submit. Everything up to Palomar's local checks needs no permission. Each later step needs the
user's explicit go-ahead: creating the repository, pushing, making it public, running the preflight
(confirm the authorization relationship first), submitting and registering. Submit only a commit
whose preflight report says `status: pass`. The preflight does not render the Challenge. Palomar
renders it after verification, with the documentation tool Verso, so check the dependency pins that
rendering needs before you submit (`references/palomar.md`, Section 1). Registering publishes
Palomar's review permanently: show the user the review, and register only when they decide to.

## Bundled tools

Run the scripts from the project root, as `python3 <skill-dir>/scripts/<name> …`. Copy the ones
that CI runs into the project's `scripts/` directory.

| Tool | Use |
| --- | --- |
| `scripts/check_file.py FILE [--autosorry]` | check one file with the lakefile's options; with `--autosorry`, replace failing proofs with `sorry` until the file elaborates |
| `scripts/autosorry.py FILE LOG` | the replacement step on its own, given Lean's output |
| `scripts/to_module.py FILE…` | convert files to the module system |
| `scripts/stmt_diff.py REV [PATH…]` | list the declarations whose statements or definitions changed since `REV` |
| `scripts/strip_unused.py LOG [--dry-run]` | delete the binders that the unused-variables linter reports |
| `scripts/strip_call_args.py [REV] [--dry-run]` | delete, at every call site, the arguments of binders removed since `REV` (default `HEAD`); run it once per cleanup round, right after `strip_unused.py`, with the commit that started the round |
| `scripts/snapshot_check.py take DIR` / `check DIR FILE [--emit]` | check files against a private copy of the build outputs, so that parallel agents do not break each other's imports |
| `scripts/session_stats.py [TRANSCRIPT…] [--since TIME] [--until TIME]` | the run log's figures (elapsed time, models, sub-agents, the most running at once, agent time, tokens, tool calls) from Claude Code session transcripts, for the whole run or for one round |
| `scripts/linkify_docs.py [--check]` | link the Lean names in the documents to their lines; copy it into the project and configure its first block |
| `scripts/check_md_tables.py FILE… [--fix]` | find, or fix, Markdown table rows broken by a `\|` inside a cell; copy it into the project |
| `scripts/route_check.py extract TEX…` / `check ROUTES [--accept FILE]` | record which results each of the paper's proofs cites; compare these with the routes of the formal proofs that the audit writes, and fail on any difference not recorded with its reason; copy it into the project |
| `scripts/sync_challenge_defs.py [--check]` | copy the block of shared definitions from a library module into `Challenge.lean`, or check that the copy is up to date (`references/palomar.md`, Section 2); copy it into the project and configure its first block |
| `assets/Audit.lean` | the axiom and dependency audit, which also writes the route of every numbered result for `route_check.py`; copy it to `scripts/Audit.lean` and fill in its lists |
| `assets/lean_action_ci.yml` | CI: build, the audit's imports, audit, route check, the Challenge's copy of shared definitions, links, tables |
| `assets/palomar_preflight.yml` | Palomar's mechanical preflight, run on demand |

## Run log

Keep an untracked log (for example `notes/runlog.md`) from Phase 0. Record:

- the start time with its time zone, and when each phase ends (the milestone commits record the
  latter);
- the agent and harness with their versions, the model(s), and this skill with its repository and
  version or commit;
- each sub-agent: what it worked on, when it started and finished, and how often it was resumed.

From the log, report the elapsed time to the audited formalization: from the start to the commit
that completes `REPORT.md` (`CREDITS.md`, which reports this time, comes in a later commit). Also
report the number of sub-agents and the most that ran at once, their total working time, and their
tool calls and tokens (output, input and cache reads, separately). Where the platform keeps session
transcripts, take these figures from them: the summaries shown when an agent finishes may measure
something else. For Claude Code, `scripts/session_stats.py` computes them. Pass every transcript if
the work spanned several sessions, and `--until` with the time of the commit that completes
`REPORT.md`. When the user asks for more work later, log each round the same way, and get its
figures with `--since` and `--until` at its start and end. Put the figures in `CREDITS.md`, one
section per round (`references/credits.md`), and in `formalization.yaml` (`automation.methods`:
`models`, `framework`, `tool_setup`, `cost`). Put the elapsed time and the number of running agents
in status reports.

## Status reports

When you report progress, use this form, and fill in only what applies:

```text
repository / branch / head:
phase:
elapsed:          time since the start; sub-agents running / finished
build:            passes / fails (first error)
sorry / axiom:    counts (excluding Challenge.lean)
statements:       changes to paper results (only documented ones), helper lemmas found false
proofs:           departures from the paper's proofs, each with its reason (reported every time
                  until the user has seen it); route-check differences still open
stage 1 / 2:      remaining internal / cited results; results assumed as hypotheses
audit:            findings so far (E-items)
packaging:        Comparator, Palomar checks, preflight
needs from user:  decisions or permissions
```

## Completion gates

- **Statements:** every numbered result stated; Challenge written, with the main results only and
  within Palomar's size limits; independent review of the statements against the paper done;
  representation bridges proved; baseline committed.
- **Stage 1:** every internal result proved by the paper's argument; cited results isolated in
  `External/` with citations.
- **Stage 2:** every cited result proved or derived from a library, or, when out of reach, a
  declared hypothesis named after its source; zero project axioms.
- **Proof routes:** `docs/paper_routes.tsv` committed and checked against the paper; the route
  check passes on the final commit, and every difference it records has its reason; every
  departure from the paper's proofs is necessary (Rules) and reported in its docstring, in the
  report's table of departures, in `formalization.yaml` and to the user; someone other than the
  provers compared the formal proofs with the paper's.
- **Verification:** clean build; `scripts/Audit.lean` passes for every declaration; `Solution.lean`
  and `comparator.json` written, and Comparator accepts the solution; no assumption hidden in a
  parameter; every structure or class of hypotheses has an instance, or the reason it cannot have
  one yet is recorded.
- **Cleanup:** the build prints only the Challenge's `sorry` warnings; unused hypotheses removed,
  and those of paper results recorded; misleading names fixed; the route check passes as before.
- **Documentation:** `REPORT.md`, `README.md` and `CREDITS.md` written, links up to date, tables
  valid, findings checked against the source; every departure from the paper's proofs listed in the
  report and the README's summary; `CREDITS.md` reports the procedure, the agents and models, the
  elapsed time and the effort from the run log, round by round, and the README's credits sum it up
  in a few lines with a link; the README kept short; earlier formalizations cited; a draft's own
  notes deleted; a conditional formalization says so in the README's first paragraph, in
  `formalization.yaml` and in the report, which lists what it assumes; the report's "What's next"
  section written from a dated search for the work that followed the paper (or, without network
  access, saying that no search could be made), with every source linked and its summary checked
  against it, and with every simpler argument recorded during the work checked and either listed
  or set aside as wrong.
- **Packaging (unless declined):** `formalization.yaml` written; Palomar's metadata and source
  checks pass on a clean clone; the dependencies shared with Verso pinned at Verso's revisions for
  the toolchain; with the user's permission for each step, the repository published, CI passing,
  and the preflight reporting `status: pass` on the exact commit to submit; the user decides about
  submission and registration.
