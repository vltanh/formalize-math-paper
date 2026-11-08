---
name: formalize-math-paper
description: >-
  Formalize a mathematics research paper in Lean 4 with Mathlib, end to end, in any area of
  mathematics: inventory the paper, state each result faithfully, prove the paper's own results and
  then the results it cites, make an existing Lean draft (often AI-written and never compiled) build
  with no sorry or axiom, audit the paper against the formalization in a report, explore which
  follow-up papers it could lead to, and package the project for the Palomar registry
  (Challenge/Solution, Comparator, formalization.yaml). Use this skill whenever the user wants to
  formalize, verify, port, repair, finish or audit a Lean formalization of a paper, preprint, arXiv
  link or list of numbered theorems; asks to "make this Lean draft compile" or to remove its
  sorries or axioms; wants a Lean project ready to submit to Palomar; or asks what paper to write
  next after a formalization, even if they name only one of these steps.
license: Apache-2.0
compatibility: >-
  Any agent that supports Agent Skills (SKILL.md), such as Claude Code, Codex, Gemini CLI,
  Antigravity, GitHub Copilot or Cursor. Needs a shell, git, Python 3 and a Lean 4 toolchain
  (elan), plus the GitHub CLI and bubblewrap to publish and to run Comparator. Parallel sub-agents
  help but are optional.
metadata:
  author: The-Anh Vu-Le
  version: "3.4.0"
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
- a private `NEXT.md`, never published unless the user asks, answers what paper the user could
  write next following this one: a few candidates that would each make a paper of their own,
  explored in depth (the obstacle, the attempts, the evidence, what is already proved), not a
  list of incremental extensions;
- the project is packaged for Palomar and, with the user's permission, published and run through
  Palomar's preflight.

The work has two stages. In Stage 1, formalize everything the paper itself proves. Results it takes
from the literature may be temporary axioms. In Stage 2, remove those axioms: prove them, or
turn the ones out of reach into stated hypotheses. Setup comes before the two stages, and
verification, cleanup, the audit and packaging come after.

## Principles

These explain the rules below. Use them when no rule covers a situation.

- The paper is the source of truth for statements and arguments; Lean judges correctness. A
  statement that differs from the paper's is a wrong formalization, however clean its proof. So is
  a proof that reaches the paper's statement by another argument: the formalization checks the
  paper's proofs, not only its claims. Review statements against the TeX source before anyone
  proves them, compare proofs with the paper's once written, and never change either silently.
- A formalization nobody has compiled is a draft. Lean written from memory and never compiled
  often has guessed lemma names, wrong signatures and false helper lemmas. Compile whenever a Lean
  toolchain is available. If none is, or the user forbids compiling, say plainly that the result
  is unverified.
- "Standard", "obvious", "by symmetry" and "routine" still need proofs. Mathlib may have the fact;
  if not, prove it. Only what the paper itself takes from another source may become an axiom.
- External means where a result comes from, not that it is trusted. A cited result lives in
  `External/` because of its source, and it is proved like everything else.
- An assumption is an assumption, whatever its form. A cited result that is not proved is assumed,
  whether it is written as an axiom, a hypothesis or a field of a structure. Axioms are not
  allowed. Hypotheses are allowed when a reader of the statement can see each one, under the name
  of the result it assumes. A structure that mixes data with assumed theorems hides what a result
  depends on. So does a parameter whose type looks like data but holds a theorem.
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
  proofs against the paper's, of the findings, of the report's account of the literature, of the
  follow-up candidates) is made by someone other than the writer: a separate agent when the
  harness has them, otherwise a separate pass of your own that starts again from the TeX source
  rather than from your notes. "An independent check" below means this.
- Report honestly. If a step was skipped, a proof fails, a statement had to change, or a proof
  had to depart from the paper's, say so and give the reason. The audit is useful only if it can be
  trusted.
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
  2. the step needs mathematics that Lean lacks and that the project cannot reasonably build (as
     for cited results out of reach, below), and another argument avoids it;
  3. the step has no meaning in a representation that the formalization must use (Principles), so
     a faithful translation of it is a different argument.

  A shorter, more elegant, more general or more automatic proof is not a reason. Neither is a proof
  that is easier to formalize or faster to build. A simpler argument that you find is still worth
  keeping: record it, with a sketch, for the report's "What's next" section (Phase 8), and prove
  the result by the paper's argument. Depart as little as the reason requires: repair the step,
  not the proof. If a departure would replace the whole argument of a numbered result, propose it
  to the user first, with the reason; other work continues meanwhile.
- Report every departure, always. For each one, record what the paper does, what the
  formalization does instead, and which reason forces the change: in the declaration's docstring
  ("Departure from the paper: …"), in the report's table of departures, in `formalization.yaml`
  (`fidelity.divergences`), in any companion text, in the route check's file of recorded
  differences when the route changes, and in the next status report. A departure missing from any
  of these is a defect: find and fix it as you would a statement that was changed silently.

### Cited results out of reach

A cited result may need mathematics that no Lean library has. If building that mathematics in the
project is a moderate effort, build it. Otherwise the default is a conditional formalization: the
result becomes a named hypothesis of every statement whose proof uses it. Apply the default without
asking, and report it in the next status report. Ask the user only when building the missing
mathematics would be a large but feasible effort: whether to spend that effort is their decision.
Meanwhile, continue the other work under the default. If they choose to build it, plan the work in
layers. Each layer replaces some hypotheses with constructions and proofs from more basic ones, and
ends in a state that can be released. These hypotheses are the only ones that may be added to a
paper result without a counterexample. Never present a conditional formalization as complete: its
README, `formalization.yaml` and report say that it is conditional and list what it assumes.

### Lean

- At the end there is no `sorry` (outside `Challenge.lean`), `admit`, `axiom`, `native_decide` or
  `implemented_by`. `native_decide` adds an axiom, which Comparator rejects.
- Never guess a Mathlib name or signature. Grep the pinned sources in `.lake/packages/mathlib`,
  or use `#check`, `exact?` and Loogle. Mathlib often renames and deprecates declarations, and
  deprecation warnings name the replacement.
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
- Keep a run log from the start ("Run log", below).

## Workflow

| Phase | Goal | Done when |
| --- | --- | --- |
| 0. Configure | record the task, ask the open questions | configuration recorded |
| 1. Inventory | know the paper: its results, definitions, constants, citations and where their proofs can come from, suspected typos | working checklist complete |
| 2. Project | a Lean project on a Mathlib release, with the module system, laid out by paper section | `lake build` runs |
| 3. Statements | every definition and numbered result stated, with `sorry` proofs; the Challenge | statements elaborate and pass an independent check against the paper; baseline committed |
| 4. Stage 1 | prove everything the paper proves, by the paper's proofs | only cited results remain, as axioms in `External/`; every departure reported |
| 5. Stage 2 | prove the cited results | zero axioms; every result still assumed is a named hypothesis |
| 6. Verify | axiom audit, dependency table, route check, Solution and Comparator | `scripts/Audit.lean` and the route check pass; proofs compared with the paper's; Comparator accepts |
| 7. Cleanup | no warnings, no unused hypotheses, no misleading names, routes unchanged | the build shows only the Challenge's `sorry`s; the route check still passes |
| 8. Audit | `REPORT.md`, `README.md`, `CREDITS.md`; the private `NEXT.md` | every finding checked against the TeX source; every follow-up candidate checked for novelty and against the bar |
| 9. Package | CI, Palomar files and checks; publishing and preflight, with permission | Palomar's local checks pass; after publishing, the preflight reports `status: pass` |

Commit at each milestone, with a message that says what changed and why.

### Phase 0: Configure

Record these. Ask the user only about what you cannot work out yourself:

```text
paper:            arXiv id and version (or DOI); source TeX if available; later versions and errata
repository:       new or existing; work on a branch and commit in small, coherent steps
starting point:   from scratch, or an existing draft (where?)
Lean / Mathlib:   the newest Lean release or release candidate (at least Palomar's minimum), and
                  Mathlib's release tag for it, unless the user pins a version or a library the
                  project needs requires a specific Mathlib commit
libraries:        the public libraries beyond Mathlib that prove results the paper cites
                  (references/palomar.md, Section 1, says which may appear in statements)
packages:         none by default; a package of its own for a famous result is proposed during the
                  inventory, and the user decides (references/separate-packages.md)
out of reach:     cited results that no library supports and the project cannot build, and how
                  each is handled (Rules)
compile allowed:  yes (the default whenever a toolchain exists)
publishing:       push? create a repository? make it public? (default: ask each time)
target:           Palomar packaging (default yes; skip it only if the user declines)
authors:          the human author(s) and maintainer(s), and the license (Apache-2.0 if not given)
run log:          the start time with its time zone, the agent, model and procedure (this skill with
                  its repository and version), recorded now
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
- every numbered result, and every displayed equation that a later proof refers to;
- constants, conditions on the parameters (ranges, "n large enough"), "without loss of generality"
  reductions, and where each constant is chosen (does `∃ C` come before or after `∀ p`?);
- which results each proof uses. This dependency graph decides the file layout and the parallel
  work in Phase 4, and it is the route that each formal proof must follow. Extract it from the TeX
  source with `scripts/route_check.py extract` into `docs/paper_routes.tsv`, read its warnings,
  compare the file with your own reading, add by hand the rows that it cannot see
  (`references/tools.md`, Section 2), and commit it;
- each citation, marked as used in a proof or only for context. For each one used in a proof, note
  where its proof can come from: Mathlib, another public library, the project itself, or nowhere
  yet, because the mathematics it needs is missing from Lean. Survey the libraries before you
  decide, and decide now how to handle the last kind (Rules), because it sets the scope. If the
  project must build a famous result that no library has, check it against the bar in
  `references/separate-packages.md`, and propose a package of its own to the user only if it
  clears it;
- suspected typos, inconsistencies and gaps, with the TeX line, and the corrections that errata or
  later versions make (Phase 0). These become the audit's E-items, so record them as you go. Settle
  a correction that changes a statement before the baseline (Phase 3, Rules);
- the paper's account of earlier and concurrent work (its introduction and remarks): the history
  of the problem, the results it builds on or improves, and the work it calls independent. It is
  the starting point of the report's literature section (Phase 8);
- the paper's open questions, conjectures and remarks on what its method could give, and the
  hypotheses it says it needs only for its method. They are the starting point of the report's
  "What's next" section and of the follow-up papers in `NEXT.md` (Phase 8).

### Phase 2: Project

Read `references/lean-project.md` for the details: versions, `lakefile.toml` (with placeholder
`Challenge.lean` and `Solution.lean` files from the start), the module system (Palomar requires it
in every `.lean` file, scripts included), building, and the layout of the project.

The project has three libraries, in layers, each importing only Mathlib, the layers below it and
itself: `Basic`, general mathematics, filed by field as Mathlib files it and named as Mathlib would
name it, so that it can be contributed later; `External`, the results of other works that the
paper cites, one directory per source, stated in the source's own terms; and `PaperName`, the
paper's own results, arranged by section. Arrange the files by the mathematical dependency graph,
not by size, and let each module import only what it uses: an edit then rebuilds only what depends
on it, and parallel work does not stall. Decide where each file belongs when you create it, cited
results included: moving files later rewrites imports, namespaces, the audit's list of modules and
the documents' links, and conflicts with every branch that touches them.

One project may formalize two closely related papers, such as a paper and the one that sharpens
it. Give each paper its own directory, keep the routes of both in the one `docs/paper_routes.tsv`
(their labels must not collide), and number the report's findings through both papers in order.

Rarely, a theorem known by name that no library has and that others would import deserves a Lake
package of its own, required at a pinned commit. The default is not to split.
`references/separate-packages.md` gives the bar, one package per area, and what such a package must
be: it stands alone, with no provenance and no reference back to the project.

Name declarations after the paper's numbering (`theorem1_2`, `lemma3_4`, `equation3_1`), so that
readers and scripts can find them. Begin the docstring of every numbered result with its number and
its TeX label in backticks (``**Theorem 1.2** (`thm:main`).``): the route check uses these labels
to find the paper's results in the Lean code. Keep every file under 10,000 lines, Palomar's limit.

### Phase 3: Statements first

Write every definition, and the statement of every numbered result and reused equation, with
`sorry` proofs. Make the whole project elaborate. Errors in statements are the most expensive kind,
and proofs can safely be done in parallel only once the statements are fixed.

For an existing draft, `scripts/autosorry.py` replaces each proof that fails to elaborate with
`sorry`. Fix errors in statements by hand. Repeat until every file elaborates, then commit ("Make
every statement elaborate").

Write `Challenge.lean`: the paper's main results, and only those, restated with `sorry` proofs in
Mathlib's vocabulary (`references/palomar.md`, Sections 1 and 2, says which other libraries Palomar
allows, and at what cost). The Challenge is the statement of record: a reader can check it without
reading the rest of the project, and Palomar trusts it because it imports nothing beyond the
libraries that Palomar allows. Intermediate results stay proved in the library, linked from the
README. Plan its size from the start: Palomar allows at most 1,000 lines and prefers 300,
definitions included. When it defines an object that a reader cannot recognize at a glance, add a
compared theorem that ties the object to something known about it, such as a known numerical
value, so that readers and Palomar's review can tell that the definition is the intended one. A
conditional result shows every assumed result in the signature of each theorem that uses it.

Then review every statement, including the Challenge's, against the TeX source, with the list in
`references/checklists.md`, Section 1, and prove a bridge lemma for each representation choice.
Have the statements and the Challenge checked independently (Principles), then commit. This commit
is the baseline. Later changes to statements are measured against it, and after it a statement
changes only by a documented decision.

### Phase 4: Stage 1, the paper's own results

Prove everything the paper proves by the paper's proof (Rules, "Faithful proofs"). When a proof
step has a typo or a slip, formalize the intended argument and record the slip as an E-item. When a
step fails, repair that step, keep the rest of the paper's argument, and report the departure. In
both cases the statement does not change.

Results the paper takes from the literature may be stated as axioms in `External/Topic/`. Give
each one its citation, its theorem or equation number, the exact special case used, and a stable
name. Put every cited result there from the start, including facts the paper uses only in a
special case, and state it in the source's terms, like the theorem that will replace it, so that
proving it in Stage 2 changes no statement of the paper's library.

When a result needs an argument that the paper does not give (an unproved theorem, a gap in a
proof, a numerical claim), work out the mathematics before you assign it. Reduce it to steps that
can be checked, test the steps numerically, and give the agent the plan and the numbers.
`references/numerics.md` covers rigorous numerics in Lean.

For more than a handful of `sorry`s, split the work into groups of files, in dependency order, for
parallel sub-agents if your environment has them, or to work through one group at a time.
`references/parallel-repair.md` has the procedure, an agent brief to copy, and the checklist for
integrating the results. Give each agent the TeX of the paper's proofs of its results. Agents
sometimes change statements, or argue differently from the paper, without reporting it: compare
every declaration's statement with the baseline (`scripts/stmt_diff.py`), and every route with the
paper's (Phase 6). Add the simpler arguments that agents report to the checklist, with yours.

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
4. If neither is feasible, follow the rule on cited results out of reach: by default the result
   becomes a proposition in `External/Topic/`, named after its source, with no proof, and a
   hypothesis of every statement whose proof uses it, the Challenge's included (several may be
   bundled in a class of hypotheses, written in each theorem's signature). The topic's `README.md`
   says what Lean lacks. If the user chose to build the missing mathematics, write down the layers
   first, and keep the end state of every layer releasable.

At the end, the project has no axioms, and every cited result is either proved or, when out of
reach, a declared hypothesis.

### Phase 6: Verify

- `lake build`: no errors, and no `sorry` warnings outside `Challenge.lean`.
- Copy `assets/Audit.lean` to `scripts/Audit.lean`, fill in its lists, and run
  `lake env lean scripts/Audit.lean`. It checks the axioms of every declaration of the library, of
  the paper's results and of the Challenge theorems. It also lists which cited results each paper
  result uses (the dependency table for the report). Under the module system it needs `import all`
  for every module; the template explains why.
- Then run the route check, `python3 scripts/route_check.py check docs/paper_routes.tsv --accept
  docs/route_differences.tsv`, always right after the audit: it compares the routes of the formal
  proofs, which the audit writes to `.lake/route_deps.tsv`, with the routes of the paper's proofs,
  and an older file would hide every proof changed since. It reports any result whose proof does not
  use a result that the paper's proof cites, or uses one that the paper's argument never reaches.
  Settle every difference: change the Lean proof to follow the paper, or, if the difference is a
  necessary departure (Rules) or a use that the paper leaves implicit, record it with its reason in
  `docs/route_differences.tsv` (and report a departure everywhere the Rules say). The check sees
  which results a proof uses, not how it argues, so also have the formal proofs compared with the
  paper's, against the TeX, independently of their provers (Principles): at least every proof that
  is long, that was written in parallel, or that changed since the last comparison.
- Complete `Solution.lean`, which restates each Challenge theorem word for word and proves it from
  the library, and write `comparator.json` (`references/palomar.md`, Sections 2 and 3). Then run
  `lake comparator` (it needs bubblewrap; see `references/palomar.md`, Section 5).
- A passing build proves only what the statements say. Go through the questions in
  `references/checklists.md`, Section 2: hidden assumptions, vacuous statements, hypotheses
  stronger than the paper's, exact index sets and constants.

### Phase 7: Cleanup

Read `references/cleanup.md`: remove unused hypotheses and then the arguments that call sites still
pass for them, in rounds that each start from a commit; fix the remaining warnings; rename files and
namespaces whose names mislead; move general lemmas that grew inside the paper's files to `Basic/`,
and cited results to `External/`. Removing an unused hypothesis of a paper result makes the Lean
statement more general than the paper's: record it for the audit. Challenge statements keep the
paper's hypotheses, except an assumed result that no proof uses, which is removed everywhere.

Cleanup changes how proofs are written, never which argument they make. Merging duplicate helpers,
shortening proofs and splitting files can change a proof's route without changing any statement,
so rerun the route check after every round. A new difference after a cleanup is a regression to
undo, not a departure to record.

### Phase 8: Audit report and documentation

Read `references/audit-report.md`: how to check findings, the structure of `REPORT.md`, the
README (rewritten whole at the end of each round, for the current state, short and in tables), and
links and tables. `references/credits.md` covers `CREDITS.md`. Start from what the earlier phases
recorded: the slips and gaps noted while reading and proving, and the hypotheses that the cleanup
removed.

The report analyzes the paper and the current formalization; it is not a history of the repair. It
lists every departure from the paper's proofs, with its reason, and the README says in one sentence
whether the proofs follow the paper's and links to that list. Every claim about the paper is checked
against the TeX source, and every arithmetic claim recomputed, independently of whoever recorded it
(Principles): a wrong error report costs more trust than a missed typo. This check often overturns
some of the inventory's own claims, and can show that a statement was changed without need. When it
does, restore the paper's statement, rerun the Phase 6 checks, and update the Challenge and the
report to match. A conditional formalization says so in the README's first paragraph, and the
report lists every assumed result.

The report ends with two sections, checked like the findings: the paper in the literature (the work
before it, alongside it and after it, and its formalizations, from the paper's own account and a
dated search, including for newer versions of the paper), and "What's next" (how the results could
be extended, generalized or strengthened, and the simpler arguments recorded during the work).
Later work that corrects the paper is also a finding: record it, and tell the user at once.

Then write the private `NEXT.md`: the papers the user could write next, following
`references/next-papers.md`. Only directions that would make a paper of their own pass its bar;
explore the best few in depth, mark each claim as proved, checked or conjectured, and have each
candidate checked independently. Keep `NEXT.md` and its scratch files out of git, of every package
and pull request, and of the public report, which only says that the file exists.

### Phase 9: Package and publish

Package for Palomar unless the user declined in Phase 0. Read `references/palomar.md`: the required
files, `formalization.yaml`, Palomar's validation scripts, CI (`assets/lean_action_ci.yml`) and the
preflight workflow (`assets/palomar_preflight.yml`). Everything up to Palomar's local checks needs
no permission; each later step needs the user's explicit go-ahead (Rules), and the preflight also a
confirmed authorization relationship. Submit only a commit whose preflight report says `status:
pass`, after checking the dependency pins that rendering with Verso needs (`references/palomar.md`,
Section 1). Registering publishes Palomar's review permanently: show the user the review, and
register only when they decide to.

## Bundled tools

`scripts/` has the project's mechanical tools, run from the project root as
`python3 <skill-dir>/scripts/<name> …` (each prints its usage with `--help`), and `assets/` has
the audit (`Audit.lean`) and the CI and preflight workflows. `references/tools.md` says what each
does, which to copy into the project, and how to complete the routes that `route_check.py`
extracts.

## Run log

Keep an untracked log (for example `notes/runlog.md`) from Phase 0: the start time with its time
zone, the agent, harness, model(s) and this skill's version, each sub-agent (task, start, end,
resumptions), and the end of each phase. `references/credits.md`, Section 1, says what figures to
report and how to take them from the session transcripts; they go in `CREDITS.md`, one section per
round, in `formalization.yaml` and in status reports.

## Status reports and completion

When you report progress, use the form in `references/checklists.md`, Section 3, and fill in only
what applies. The work is done when every gate in Section 4 there is met (statements, Stage 1 and
2, proof routes, verification, cleanup, documentation, follow-up papers and packaging): go through
them before you report the work as finished.
