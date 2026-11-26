---
name: formalize-math-paper
description: >-
  Formalize a mathematics research paper in Lean 4 with Mathlib, end to end, in any area of
  mathematics: inventory the paper, state each of its claims faithfully, prove the paper's own
  results and then the results it cites, make an existing Lean draft (often AI-written and never
  compiled) build with no sorry or axiom, audit the paper against the formalization in a report,
  explore which follow-up papers it could lead to, and package the project for the Palomar registry
  (Challenge/Solution, Comparator, formalization.yaml). Use this skill whenever the user wants to
  formalize, verify, port, repair, finish or audit a Lean formalization of a paper, preprint, arXiv
  link, list of numbered theorems or proof of their own; asks to "make this Lean draft compile" or
  to remove its sorries or axioms; wants a Lean project ready to submit to Palomar; or asks what
  paper to write next after a formalization, even if they name only one of these steps.
license: Apache-2.0
compatibility: >-
  Any agent that supports Agent Skills (SKILL.md), such as Claude Code, Codex, Gemini CLI,
  Antigravity, GitHub Copilot or Cursor. Needs a shell, git, Python 3 and a Lean 4 toolchain
  (elan), plus the GitHub CLI and bubblewrap to publish and to run Comparator. Parallel sub-agents
  help but are optional.
metadata:
  author: The-Anh Vu-Le
  version: "4.8.1"
  repository: https://github.com/vltanh/formalize-math-paper
---

# Formalizing a mathematics paper in Lean 4

You deliver a Lean project in the standard layout (`references/lean-project.md`; for one paper,
the Lean code under `PaperName/`, the Palomar files in `palomar/PaperName/` and the documents in
`docs/PaperName/`), in which:

- every claim of the paper is stated and proved: its numbered results, and also its remarks,
  examples, uniqueness claims, the consequences it asserts and the claims it makes in running text,
  whether or not another proof uses them. Each is proved by the paper's own argument where the paper
  gives one. A proof departs from the paper's only when it must, and every departure is reported
  (Rules, "Faithful proofs");
- every result the paper cites in its proofs is proved too: in Mathlib, in another public library,
  or in `PaperName/External/`, from a package of the project's own when it needs a theory that no
  Lean library has (Rules, "Mathematics that Lean lacks"). A cited result stays assumed only if the
  user decides so or there is no proof of it to formalize. It is then a named hypothesis of every
  statement that uses it, and the formalization says plainly that it is conditional;
- the statements say what the paper says, and every deviation is documented;
- `lake build` succeeds with no `sorry` (except in the Challenge's proofs, by design), no
  `admit` and no project `axiom`. Every declaration of the library depends only on `propext`,
  `Classical.choice` and `Quot.sound`;
- `docs/PaperName/REPORT.md` audits the paper against the formalization, and ends with the paper's
  place in the literature and what comes next (extensions, simpler proofs). `README.md`, at the
  root, summarizes the formalization, and `docs/PaperName/CREDITS.md` says how it was made: the
  procedure, the agents and models, and the time and effort (the run log);
- a private `notes/follow-up-papers.md`, never published unless the user asks, explores in depth a
  few papers that the user could write next, each a paper of its own, not an incremental extension;
- the project is packaged for Palomar, in `palomar/PaperName/`, and, with the user's permission,
  published and run through Palomar's preflight.

A repository may formalize several related papers (a theorem and its sequel, complementary cases of
one problem, a claim and its refutation). Their code is then under one root named after the
project, with the shared code in `ProjectName/Common/`, and they add an umbrella README, rules for
results that cross papers, and one Palomar submission per paper (`references/multi-paper.md`).

The mathematics may also be the user's own: a result with no published paper behind it. The
workflow's mechanics still apply, but there is no paper to audit or to follow;
`references/original-results.md` says what changes.

A project's own instructions (`CLAUDE.md`, `AGENTS.md`, or a conventions document that they point
to) take precedence over this skill's defaults, and may already settle some of Phase 0's questions.
Read them first.

The work has two stages. In Stage 1, formalize everything the paper itself proves. Results it takes
from the literature may be temporary axioms. In Stage 2, remove those axioms by proving them,
building any theory that their proofs need and Lean lacks. Setup comes before the two stages, and
verification, cleanup, the audit and packaging come after.

## Principles

These explain the rules below. Use them when no rule covers a situation.

- The paper is the source of truth for statements and arguments; Lean judges correctness. A
  statement that differs from the paper's is a wrong formalization, however clean its proof. So is
  a proof that reaches the paper's statement by another argument: the formalization checks the
  paper's proofs, not only its claims. Every claim is part of what the paper says, whether or not
  its other proofs use it. Review statements against the TeX source before anyone proves them,
  compare proofs with the paper's once written, and never change either silently.
- A formalization nobody has compiled is a draft. Lean written from memory and never compiled
  often has guessed lemma names, wrong signatures and false helper lemmas. Compile whenever a Lean
  toolchain is available. If none is, or the user forbids compiling, say plainly that the result
  is unverified.
- "Standard", "obvious", "by symmetry" and "routine" still need proofs. Mathlib may have the fact;
  if not, prove it. Only what the paper itself takes from another source may become an axiom.
- Missing mathematics is work to do, not a reason to do something else. A proof of the paper's step
  that avoids it checks a different argument, and a hypothesis in its place leaves the paper's
  claim unchecked. Theory that others could use goes in a package of its own, so that the work
  outlasts the project.
- External means where a result comes from, not that it is trusted. A cited result lives in
  `External/` because of its source, and it is proved like everything else, by an argument that its
  docstring names (Rules).
- An assumption is an assumption, whatever its form. A cited result that is not proved is assumed,
  whether it is written as an axiom, a hypothesis or a field of a structure. No axiom remains at the
  end. Hypotheses are allowed when a reader of the statement can see each one, under the name of the
  result it assumes. A structure that mixes data with assumed theorems hides what a result depends
  on. So does a parameter whose type looks like data but holds a theorem.
- Data comes with its defining property. When a statement takes an object of the paper as a
  parameter instead of constructing it, it must also require the property that defines the object.
  Otherwise the theorem is about every object that satisfies the other hypotheses, which is a
  different statement.
- Representation choices need bridges. Lean's objects may differ from the paper's: indices from 0
  instead of 1, lists instead of indexed families, a bundled Mathlib structure instead of an
  informal object, a concrete model instead of a description "up to isomorphism". When they do,
  prove a lemma that connects the two, and document the choice. Never assume two representations
  are equivalent.
- Constants and ranges are part of the mathematics. Powers, factors, floors, ceilings, strict
  versus weak inequalities, the endpoints of ranges and truncated subtraction on `ℕ` decide
  whether a statement is true.
- Writers miss their own errors. Every check that the workflow asks for (of the statements, of the
  proofs against the paper's and against the sources they are attributed to, of the findings, of the
  report's account of the literature, of the follow-up candidates) is made by someone other than the
  writer: a separate agent when the harness has them, otherwise a separate pass of your own that
  starts again from the TeX source rather than from your notes. "An independent check" below means
  this.
- Report honestly. If a step was skipped, a proof fails, a statement had to change, or a proof
  had to depart from the paper's, say so and give the reason. The audit is useful only if it can be
  trusted.
- Every text describes the current state. A document, docstring or comment reads as if it had always
  said what it says. It mentions another project only when it uses something from it or cites it as
  related work, and a dependency never names the projects that use it. The history of the work
  belongs in commit messages and `CREDITS.md` (`references/audit-report.md`, Section 4).
- A gap in a proof is not a false statement. When the paper's proof uses a fact that its
  hypotheses do not give, the statement may still be true. Look for a correct argument before you
  conclude anything about the statement.
- Measure the work. Readers and registries ask how a formalization was made. The answer is cheap
  to record as you go, and hard to reconstruct afterwards.

## Rules

### Statements

- Never weaken or change the statement of a paper result to make a proof work. If the paper's
  statement is false, stop work on it and tell the user at once, with the counterexample; other
  work can continue meanwhile. If the user agrees, formalize the closest correct version and record
  it as an error in the report. Obvious misprints are the one exception (below).
- Never add a hypothesis to a paper result because its proof seems to need it: adding one weakens
  the result. Add one only when the statement itself has a counterexample, not because a step of
  the proof fails, and then follow the previous rule. Otherwise prove the statement as printed, by
  a corrected argument, and record the gap in the proof as an E-item. If you find neither a proof
  nor a counterexample, tell the user what is missing. They decide whether to keep working or to
  formalize a weaker statement, documented as a deviation.
- If a statement is false only because of an obvious misprint (a wrong index, a swapped name, a
  missing `- 1`), and only one reading can be intended, formalize that reading at once, in the
  library and in the Challenge. List each such correction in the report and in the next status
  report to the user. When more than one fix is possible, treat the statement as false.
- A false helper lemma (one you or a draft introduced) needs a concrete counterexample, checked in
  Lean (`decide`, `norm_num` or `#eval`) when possible. Then add the minimal hypothesis, update its
  callers, and record the change in the commit message.

### Faithful proofs

- Prove every result by the paper's proof: the same intermediate claims, the same constructions
  and case splits, and the same earlier results where the paper cites them. The results that the
  paper's proof cites form its *route*. The formal proof must have the same route, and the route
  check (Phase 6) verifies this. Only the mechanics may differ: tactics, the Mathlib lemma that
  closes a routine step, the order of independent steps, and helper lemmas that package a step of
  the paper. If Mathlib happens to prove a numbered result, prove it by the paper's argument
  anyway, unless the paper itself treats it as known (it cites it, or calls it standard).
- Depart from the paper's proof only when you must, that is, for one of these reasons and no
  other:
  1. the paper's argument is wrong at that step, or has a gap there, and cannot be repaired along
     its own lines (the step is also an E-item);
  2. the step has no meaning in a representation that the formalization must use (Principles), so
     a faithful translation of it is a different argument.

  Lean or Mathlib lacking the mathematics that a step needs is not a reason: build that
  mathematics (below), however large. A shorter, more elegant, more general or more automatic proof
  is not a reason either, nor is a proof that is easier to formalize or faster to build. A simpler
  argument that you find is still worth keeping: record it, with a sketch, for the report's
  "What's next" section (Phase 8), and prove the result by the paper's argument. A Lean proof by
  another argument that already exists is not deleted when the paper's argument replaces it: keep
  it as a theorem of its own, attributed to its argument and outside the chain of the paper's
  proofs, and list it among the simpler proofs. Depart as little as the reason requires: repair the
  step, not the proof. If a departure would replace the whole argument of a numbered result,
  propose it to the user first, with the reason; other work continues meanwhile. The user may also
  choose a departure for reasons of their own (to release sooner, say); record it as their decision.
- Report every departure, always. For each one, record what the paper does, what the
  formalization does instead, and which reason forces the change: in the declaration's docstring
  ("Departure from the paper: …"), in the report's table of departures, in `formalization.yaml`
  (`fidelity.divergences`), in any companion text, in the route check's file of recorded
  differences when the route changes, and in the next status report. A departure missing from any
  of these is a defect: find and fix it as you would a statement that was changed silently.

### Mathematics that Lean lacks

A cited result, or a step of the paper's own proof, may need mathematics that no Lean library has:
one theorem, or a whole theory with its definitions and the results around them. Build it. Where
it goes is decided by the test in `references/separate-packages.md`: a general theory in a package
of its own, a lemma or a development that only this paper needs in `Basic/` or `External/`
(Phase 2). For a step of the
paper's own proof, keep the paper's argument.

A cited result is different: the paper uses its statement, not its proof. In the project, state it
in its source's terms, as the paper uses it (its constants, ranges and hypotheses), and check that
statement against the source. Then prove it by the cheapest sound route: a theorem of a library, a
short argument from the literature (the source's own or another one), or an argument of your own.
Name the argument in the docstring and in the report's table of cited results. Where the paper
uses more than the statement (an estimate from inside the proof, a construction, the form of a
constant), that part is the paper's argument, and it follows the source like the rest of the
paper's proofs. Ask the user for a source when you need its statement, or the part of its proof
that the paper uses, and cannot read it (try its open archives first). Do not say what a source
contains, or what its proof would need, before reading it. Record in the report's list of simpler
proofs any shorter argument that you notice and do not use.

A package of its own is a library: it formalizes the literature for others to reuse, so each result
that it attributes to a source is proved by that source's argument, and the works that the source
cites are treated alike, level by level (`references/separate-packages.md`, Section 3). Publish the
paper's formalization only when this work is done too, unless the user asks for an earlier
release: what is pushed should be finished. The project uses the package's statements like any
library's. Everywhere, in the project and in the packages, a proof attributed to a source is that
source's argument, and a proof by another argument is attributed to that argument.

The size of the work is not a reason to skip it, but the user must know it. As soon as the inventory
shows a missing theory, estimate it (what must be built, in what order, roughly how many lines),
plan it in layers, tell the user in the next status report, and start without waiting. Each layer
replaces some assumptions with constructions and proofs from more basic ones, and ends in a
consistent state, which the user may choose to release early: until the last layer, each result not
yet reached is a named hypothesis, under its source's name, of the statements that use it.

At the end, a result stays assumed only when the user decides so after seeing the plan, or when
there is nothing to formalize: its source gives no proof (a conjecture, an unpublished claim) and
none is known. These hypotheses, the temporary ones of an unfinished layer, and a weaker statement
that the user chooses (Rules, "Statements") are the only changes made to a paper result without a
counterexample. Never present a conditional formalization as complete: its README,
`formalization.yaml` and report say that it is conditional, list what it assumes, and say why each
is still assumed.

### Lean

- At the end there is no `sorry` (outside the Challenge), `admit`, `axiom`, `native_decide` or
  `implemented_by`. `native_decide` adds an axiom, which Comparator rejects.
- Never guess a Mathlib name or signature. Grep the pinned sources in `.lake/packages/mathlib`,
  or use `#check`, `exact?` and Loogle. Mathlib often renames and deprecates declarations, and
  deprecation warnings name the replacement.
- Reuse before you define. Before writing a definition or a general lemma, search Mathlib and every
  library that the project requires (their sources are in `.lake/packages`), and use what they
  have: a second definition of the same object needs a bridge, and the library's results do not
  transfer to it.
- Never edit a file under `.lake/packages`. Lake may replace it at any update, and checkouts that
  share these files through hard links (`references/separate-packages.md`, Section 4) all change
  with it. Change a dependency in its own repository, then move the pin.
- If you cannot compile (no toolchain, or the user forbids it), write the Lean without compiling
  it. Check every name, signature and import path against the pinned Mathlib sources, keep the
  statements-first order, and label every result as unverified. Whoever compiles the project later
  starts at Phase 3.
- Run one `lake build` at a time per checkout. Builds that run at the same time delete each
  other's `.olean` files, and an editor open on the project runs its own `lake setup-file` builds.
  If you see "object file … does not exist", retry instead of editing around it.

### Permissions and credit

- Ask before any action that others can see: pushing, creating a repository, changing a
  repository's visibility, opening or closing pull requests, deleting branches, running Palomar's
  preflight, submitting to Palomar, registering. Permission for one of these is not permission for
  the others.
- Authors are people. Credit AI systems in the README, in `CREDITS.md` and in the `automation`
  section of `formalization.yaml`, never as authors or maintainers.
- Before each commit, check the staged diff and the message for what must stay private: paths into
  `notes/` and the names of private files, absolute paths of this machine, and private
  repositories. `git diff --cached | grep -nE 'notes/|/home/|/Users/'` finds most of them.
- Keep a run log from the start ("Run log", below).

## Workflow

| Phase | Goal | Done when |
| --- | --- | --- |
| 0. Configure | record the task, ask the open questions | configuration recorded |
| 1. Inventory | know the paper: its results, definitions, constants, citations and where their proofs can come from, suspected typos | working checklist complete |
| 2. Project | a Lean project on a Mathlib release, with the module system, in the standard layout, the paper's library by section | `lake build` runs |
| 3. Statements | every definition and every claim of the paper stated, with `sorry` proofs; the Challenge | statements elaborate and pass an independent check against the paper; baseline committed |
| 4. Stage 1 | prove everything the paper proves, by the paper's proofs | only cited results remain, as axioms in `External/`; every departure reported |
| 5. Stage 2 | prove the cited results | zero axioms; every result still assumed is a named hypothesis |
| 6. Verify | axiom audit, dependency table, route check, Solution and Comparator | `scripts/Audit.lean` and the route check pass; proofs compared with the paper's; Comparator accepts |
| 7. Cleanup | no warnings, no unused hypotheses, no misleading names, routes unchanged | the build shows only the Challenge's `sorry`s; the route check still passes |
| 8. Audit | `README.md`; in `docs/PaperName/`, `REPORT.md` and `CREDITS.md`; the private `notes/follow-up-papers.md` | every finding checked against the TeX source; every follow-up candidate checked for novelty and against the bar |
| 9. Package | CI, Palomar files and checks; publishing and preflight, with permission | Palomar's local checks pass; after publishing, the preflight reports `status: pass` |

Commit at each milestone, with a message that says what changed and why.

### Phase 0: Configure

Record these. Ask the user only about what you cannot work out yourself or find in the project's
instructions:

```text
paper:            arXiv id and version (or DOI); source TeX if available; later versions and errata
papers:           one, or several in one repository (references/multi-paper.md; when a paper joins
                  an existing project, ask whether it joins the repository)
names:            PaperName, after the paper (its first author or a short title): the root of the
                  Lean code, and the name of its Palomar and document directories; with several
                  papers, one per paper, and ProjectName, the root of the code, after the question
repository:       new or existing; work on a branch and commit in small, coherent steps
starting point:   from scratch, or an existing draft (where?)
Lean / Mathlib:   the newest Lean release or release candidate (at least Palomar's minimum), and
                  Mathlib's release tag for it, unless the user pins a version or a library the
                  project needs requires a specific Mathlib commit
libraries:        the public libraries beyond Mathlib that prove results the paper cites
                  (references/palomar.md, Section 1, says which may appear in statements)
missing theory:   from the inventory (Phase 1): what the paper's proofs and cited results need that
                  no Lean library has, the
                  theory to build for each, its estimate, and its package (Rules; packages are
                  named for their area, references/separate-packages.md)
compile allowed:  yes (the default whenever a toolchain exists)
publishing:       push? create a repository? make it public? (default: ask each time)
target:           Palomar packaging (default yes; skip it only if the user declines)
authors:          the human author(s) and maintainer(s), and the license (Apache-2.0 if not given)
run log:          started now ("Run log", below)
earlier work:     earlier formalizations of the paper, its main result and the results it cites
```

Get the paper's TeX source (on arXiv, the "TeX Source" link), not only the PDF. Exact statements,
constants and cross-references are much easier to check in TeX.

Before starting, search for later versions of the paper (a newer arXiv version, the published
version, errata) and for earlier formalizations of the paper or of its main result (GitHub, the Lean
Zulip, the Palomar registry, collections of formal statements, the roadmaps of the large libraries).
Tell the user what you find, or that you could not search without network access. If the version you
were given is not the latest, say what the later ones change, and ask which to formalize. An earlier
formalization changes what a new one should add: the report, the README and `formalization.yaml`
cite it, and Palomar's review asks whether a submission duplicates existing work.

Starting from an existing draft, import it unchanged as the first commit. Make the commit's author
whoever wrote the draft (for an AI-written draft, the system that wrote it, with a no-reply
address), give the commit a message that only says what it is ("Uncompiled draft"), and add no
co-author trailer and none of your own edits. The draft's own notes (checklists that claim it is
complete, source maps) describe a state that nobody verified: delete them once `README.md` and
`REPORT.md` replace them in Phase 8. They remain in the history. If the draft lives elsewhere, in a
pull request or a branch of another repository, offer to close or delete it once the new repository
replaces it, and do not link to it from the deliverables.

### Phase 1: Inventory

Read the whole paper before you write any Lean. Keep a working checklist outside the deliverables
(in a scratch directory or an untracked `notes/`), with:

- definitions and notation, including implicit conventions (the base of logarithms, what `⊆`
  means, indexing);
- every claim: each numbered result, each displayed equation that a later proof refers to, and
  each mathematical claim outside them (a remark, an example, a uniqueness claim, a consequence that
  the paper asserts, a statement made in running text), whether or not another proof uses it. Give
  each claim without a label one of your own (`references/tools.md`, Section 2). Only what is not a
  mathematical claim stays out: empirical findings, announcements with no precise statement, and
  citations that only give context;
- constants, conditions on the parameters (ranges, "n large enough"), "without loss of generality"
  reductions, and where each constant is chosen (does `∃ C` come before or after `∀ p`?);
- which results each proof uses. This dependency graph decides the file layout and the parallel work
  in Phase 4, and it is the route that each formal proof must follow. Extract it from the TeX source
  with `<skill-dir>/scripts/route_check.py extract`, read its warnings, compare the result with your
  own reading, add by hand the rows that it cannot see (`references/tools.md`, Section 2), and
  commit it as `docs/PaperName/paper_routes.tsv` once the project exists (Phase 2);
- each citation, marked as used in a proof or only for context. For each one used in a proof, note
  the form the paper uses (constants, ranges, hypotheses), whether it uses more than the statement
  (an estimate from the proof, a construction, the form of a constant), and where its proof can
  come from, after surveying the libraries: Mathlib, another library, or the project, and then what
  it needs that no Lean library has. Note the same for each step of the paper's own proofs that
  uses a theory Lean lacks. Group what is missing into theories, place, estimate and plan each
  (Rules, "Mathematics that Lean lacks"): this sets the scope;
- suspected typos, inconsistencies and gaps, with the TeX line, and the corrections that errata or
  later versions make (Phase 0). These become the audit's E-items, so record them as you go. Settle
  a correction that changes a statement before the baseline (Phase 3, Rules);
- the paper's account of earlier and concurrent work (its introduction and remarks): the history
  of the problem, the results it builds on or improves, and the work it calls independent. It is
  the starting point of the report's literature section (Phase 8);
- the paper's open questions, conjectures and remarks on what its method could give, and the
  hypotheses it says it needs only for its method. They are the starting point of the report's
  "What's next" section and of the follow-up papers (Phase 8).

### Phase 2: Project

Read `references/lean-project.md` for the details: versions, the layout, `lakefile.toml` (with
placeholder Challenge and Solution files from the start), the module system (Palomar requires it in
every `.lean` file, scripts included), and building.

A project with one paper has all its Lean code under one root named after the paper, `PaperName/`,
in layers, each importing only Mathlib and the libraries the project requires, the layers below it,
and itself: `Basic/`, general mathematics, filed and named as Mathlib would, so that it can be
contributed later; `External/`, the results that the paper cites, one directory per source, in the
source's own terms; and the paper's library, by section, in the rest of `PaperName/`. The Palomar
files are in `palomar/PaperName/`, the documents in `docs/PaperName/`. Arrange the files by the
mathematical dependency graph, let each module import only what it uses, and decide where each file
belongs when you create it: moving files later rewrites imports, namespaces, the audit's list of
modules and the documents' links, and conflicts with every branch that touches them.

Several papers in one repository share `ProjectName/Common/` and keep one library each,
`ProjectName/PaperName/` (`references/multi-paper.md`). A project of one paper keeps the shortest
paths until then: when a second paper joins, the first paper's code moves to that layout once,
before the second paper's statements are written, while its Palomar files and documents stay where
they are (Section 9 there). Missing theory that passes the test in `references/separate-packages.md`
goes in a Lake package of its own, named for its area, standing alone, with no reference back to the
project, and required at a pinned commit.

Name declarations after the paper's numbering (`theorem1_2`, `lemma3_4`, `equation3_1`), and a
claim without a number after its place in the paper, so that readers and scripts can find them.
Begin the docstring of every claim with its number, when it has one, and its label in backticks
(``**Theorem 1.2** (`thm:main`).``): the route check uses these labels to find the paper's results
in the Lean code. Keep every file under 10,000 lines, Palomar's limit.

### Phase 3: Statements first

Write every definition, and the statement of every claim of the inventory and of every reused
equation, with `sorry` proofs. Make the whole project elaborate. Errors in statements are the most
expensive kind, and proofs can safely be done in parallel only once the statements are fixed.

For an existing draft, `scripts/autosorry.py` replaces each proof that fails to elaborate with
`sorry`. Fix errors in statements by hand. Repeat until every file elaborates, then commit ("Make
every statement elaborate").

Write the Challenge, `palomar/PaperName/Challenge.lean`: the paper's main results, restated with
`sorry` proofs in Mathlib's vocabulary (`references/palomar.md`, Sections 1 and 2), and besides them
only the compared theorems described below. It is the statement of record, which a reader can check
without reading the rest of the project. Plan its size from the start: Palomar allows at most 1,000
lines and prefers 300, definitions included. When it defines an object that a reader cannot
recognize at a glance, add a compared theorem that ties the object to something known about it, such
as a known numerical value. A conditional result shows every assumed result in the signature of each
theorem that uses it.

Then review every statement, including the Challenge's, against the TeX source, and each cited
result's also against its source, with the list in `references/checklists.md`, Section 1, and
prove a bridge lemma for each representation choice. Have the statements and the Challenge checked
independently (Principles), then commit. This commit is the baseline. Later changes to statements
are measured against it, and after it a statement changes only by a documented decision.

### Phase 4: Stage 1, the paper's own results

Prove everything the paper proves by the paper's proof (Rules, "Faithful proofs"). When a proof step
has a typo or a slip, formalize the intended argument and record the slip as an E-item. When a step
fails, repair it along the paper's own lines if you can, and record it as an E-item; if it cannot be
repaired so, replace that step only, keep the rest of the paper's argument, and report the departure
(Rules). In every case the statement does not change.

Results the paper takes from the literature may be stated as axioms in `External/Source/`. Give each
one its citation, its theorem or equation number and a stable name, and state it with the source's
definitions (or Mathlib's) at the generality that the paper uses: its special case, constants,
ranges and hypotheses. Put every cited result there from the start, including facts that the paper
uses only in a special case, each stated like the theorem that will replace it, so that proving it
in Stage 2 changes no statement of the paper's library.

When a result needs an argument that the paper does not give (an unproved theorem, a gap in a
proof, a numerical claim), work out the mathematics before you assign it. Reduce it to steps that
can be checked, test the steps numerically, and give the agent the plan and the numbers.
`references/numerics.md` covers rigorous numerics in Lean.

For more than a handful of `sorry`s, split the work by files, in dependency order, among parallel
sub-agents, or into groups that you work through in turn: `references/parallel-repair.md` has the
procedure, an agent brief and the checklist for integrating the results. Agents sometimes change
statements, or argue differently from the paper, without reporting it: compare every statement with
the baseline (`scripts/stmt_diff.py`) and every route with the paper's (Phase 6), and add the
simpler arguments that they report to the checklist.

### Phase 5: Stage 2, cited results

For each cited result:

1. Search Mathlib, at the pinned version, and the other public Lean libraries, formalizations of
   the cited work included. A library used only in proofs may be any pinned public repository. A
   library whose definitions the Challenge needs must be one that Palomar allows in statements
   (`references/palomar.md`, Section 1). Depending on a library can require a specific Mathlib
   commit: settle that before you build on it.
2. If the result is there, require the library rather than copying its proofs, and prove that its
   form implies exactly what the paper uses (parameters, notation, finite versus infinite, bundled
   versus unbundled). When a formalization cannot be required as it is (its module names clash with
   others, it is on another Mathlib, it does not use the module system), tell the user what would
   make it requirable, and, with the user's permission, propose that change to its maintainers. Copy
   its proofs only as a last resort, keeping its notice (`references/palomar.md`, Section 1): a copy
   drifts from its source, and the result belongs to the project that proves it.
3. Otherwise, formalize it under `External/Source/`, with a `README.md` that gives the source, the
   statement, how its Lean forms relate to the paper's use of it, and the argument that proves it,
   chosen as the Rules say ("Mathematics that Lean lacks"), and named in the docstring. Proving a
   different standard form is fine if it gives exactly the estimates the paper needs; say so.
4. Until the layer that proves it is done, the result is a proposition named after its source, and a
   hypothesis of every statement whose proof uses it, the Challenge's included (several may be
   bundled in a class of hypotheses, written in each theorem's signature). It is defined in
   `External/Source/`, or, when a Challenge theorem uses it, in the block of shared definitions
   (`references/palomar.md`, Section 2). The source's `README.md` says what is still missing and
   which layer removes it.

At the end, the project has no axioms, and every cited result is proved, except those that stay
assumed by the Rules, each a declared hypothesis.

### Phase 6: Verify

- `lake build`: no errors, and no `sorry` warnings outside the Challenge.
- Copy `assets/Audit.lean` to `scripts/Audit.lean`, fill in its lists, and run
  `lake env lean scripts/Audit.lean`. It checks the axioms of every declaration of the library, of
  the paper's results and of the Challenge theorems. It also lists which cited results each paper
  result uses (the dependency table for the report). Under the module system it needs `import all`
  for every module of the library and for the Solution, never the Challenge; the template explains
  why.
- Then run the route check, `python3 scripts/route_check.py check docs/PaperName/paper_routes.tsv
  --accept docs/PaperName/route_differences.tsv`, always right after the audit, whose
  `.lake/route_deps.tsv` it reads: an older file would hide every proof changed since. It reports
  each proof that misses a result the paper's proof cites, or uses one that the paper's argument
  never reaches (`references/tools.md`, Section 2). Settle every difference: change the Lean proof
  to follow the paper, or record in `route_differences.tsv`, with its reason, a necessary departure
  (Rules), a use that the paper leaves implicit, or a result that it cites only in passing. The
  check sees which results a proof uses, not how it argues, so also have the formal proofs compared
  with the paper's, against the TeX, independently of their provers (Principles): at least every
  proof that is long, that was written in parallel, or that changed since the last comparison, and
  each proof attributed to a source against that source.
- Complete `palomar/PaperName/Solution.lean`, which restates each Challenge theorem word for word
  and proves it from the library, and write `comparator.json` beside it (`references/palomar.md`,
  Sections 2 and 3). Then run `lake env lake comparator --config=palomar/PaperName/comparator.json`
  (it needs bubblewrap; see `references/palomar.md`, Section 5).
- A passing build proves only what the statements say. Go through the questions in
  `references/checklists.md`, Section 2: hidden assumptions, vacuous statements, hypotheses
  stronger than the paper's, exact index sets and constants.

### Phase 7: Cleanup

Read `references/cleanup.md`: unused hypotheses, and then the arguments that call sites still pass
for them, removed in rounds that each start from a commit; the other warnings; misleading names;
general lemmas moved to `Basic/`, and cited results to `External/`. Removing an unused hypothesis of
a paper result makes the Lean statement more general than the paper's: record it for the audit.
Challenge statements keep the paper's hypotheses, except an assumed result that no proof uses,
which is removed everywhere. Cleanup changes how proofs are written, never which argument they
make: rerun the route check after every round, and undo any new difference as a regression.

### Phase 8: Audit report and documentation

Read `references/audit-report.md`: how to check findings, the structure of
`docs/PaperName/REPORT.md` and of the README at the root (rewritten whole at the end of each round,
short and in tables), and the style of every document. `references/credits.md` covers
`docs/PaperName/CREDITS.md`. Start from what the earlier phases recorded: the slips and gaps noted
while reading and proving, and the hypotheses that the cleanup removed.

The report analyzes the paper and the current formalization. It lists every departure from the
paper's proofs, with its reason, and the README says in one sentence whether the proofs follow the
paper's and links to that list. Every claim about the paper is checked
against the TeX source, and every arithmetic claim recomputed, independently of whoever recorded it
(Principles): a wrong error report costs more trust than a missed typo. This check often overturns
some of the inventory's own claims, and can show that a statement was changed without need. When it
does, restore the paper's statement, rerun the Phase 6 checks, and update the Challenge and the
report to match. A conditional formalization says so in the README's opening paragraphs, and the
report lists every assumed result and why it is still assumed.

The report ends with the paper in the literature, from its own account and a dated search, and
"What's next", with the simpler arguments recorded during the work, both checked like the findings.
Later work that corrects the paper is also a finding: record it, and tell the user at once.

With several papers, each paper's documents, its README included, follow this phase for that paper
alone in `docs/PaperName/`, and the umbrella README (`references/multi-paper.md`, Section 6) gives
the state of the problem and the literature review that connects the papers, checked independently.

Then write the private `notes/follow-up-papers.md` (with several papers, one per paper,
`notes/PaperName/follow-up-papers.md`): the papers the user could write next, following
`references/follow-up-papers.md`. Only directions that would make a paper of their own pass its
bar; explore the best few in depth, and have each checked independently. The file and its scratch
files stay in `notes/`, which git ignores, and no public document mentions them.

### Phase 9: Package and publish

Package for Palomar unless the user declined in Phase 0. Read `references/palomar.md`: the files in
`palomar/PaperName/`, `formalization.yaml`, Palomar's local checks, CI (`assets/lean_action_ci.yml`)
and the preflight (`assets/palomar_preflight.yml`, whose options always name both
`comparator_config_path` and `formalization_metadata_path`). With several papers, each is a
submission of its own (`references/multi-paper.md`, Section 7), and so is each package built for
missing theory (`references/separate-packages.md`, Section 5). Everything up to Palomar's local
checks needs no permission; each later step needs the user's explicit go-ahead (Rules). Submit only
a commit whose preflight report says `status: pass`, and register only when the user, having seen
Palomar's review, decides to: registering publishes it permanently.

## Bundled tools

`scripts/` has the project's mechanical tools, run from the project root as
`python3 <skill-dir>/scripts/<name> …` (each prints its usage with `--help`), and `assets/` has
the audit (`Audit.lean`) and the CI and preflight workflows. `references/tools.md` says what each
does, which to copy into the project, and how to complete the routes that `route_check.py`
extracts.

## Run log

Keep an untracked log (for example `notes/runlog.md`) from Phase 0, with times read from the clock
(`date`), never estimated: the start time with its time zone; the agent and harness with their
versions, the model(s), and this skill with its repository and version or commit; each sub-agent
(task, start, end, resumptions); and the end of each phase. `references/credits.md`, Section 1, says
what figures to report and how to take them from the session transcripts; they go in `CREDITS.md`,
one section per round, in `formalization.yaml` and in status reports.

## Status reports and completion

When you report progress, use the form in `references/checklists.md`, Section 3, and fill in only
what applies. The work is done when every gate in Section 4 there is met: go through them before you
report the work as finished.
