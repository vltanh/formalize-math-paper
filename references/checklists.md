# Checklists: verification, status reports, completion

## Contents

1. Reviewing statements (Phase 3)
2. Questions a passing build does not answer (Phase 6)
3. The status report
4. Completion gates

## 1. Reviewing statements (Phase 3)

Review every statement, including the Challenge's, against the TeX source. Check:

- the order of quantifiers, and where constants are chosen (does `∃ C` come before or after `∀ p`?);
- strict versus weak inequalities, and the endpoints of ranges;
- casts and truncation (`ℕ` subtraction and division, `Nat.floor`);
- indexing from 0 versus 1; "max over z" versus "for every z"; whether "positive integer" became
  `ℕ`;
- the types Lean inferred where the statement does not give them;
- implicit standing assumptions;
- whether the hypotheses that a draft declares with `variable` reach the statements whose proofs use
  them (Lean leaves out of a statement every section variable that it does not mention: check with
  `#check`);
- whether every hypothesis of a statement is either the paper's or a declared assumption;
- whether each representation choice has a bridge lemma.

## 2. Questions a passing build does not answer (Phase 6)

A passing build proves only what the statements say. Ask of the formalization:

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
- Does each library theorem used for a cited result imply exactly the paper's form? Does each
  bridge from the paper's objects to a source's, in the paper's library, prove the
  identification that the paper makes, and does `External` import nothing of the paper's?
- Does each proof follow the paper's argument, and is every departure necessary and reported?
- Are sums, counts and unions taken over exactly the paper's index sets?
- Are the constants exact?

## 3. The status report

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
next papers:      the candidates in NEXT.md (private), ranked, a line each; where the file is
needs from user:  decisions or permissions
```

## 4. Completion gates

- Statements: every numbered result stated; Challenge written, with the main results only and
  within Palomar's size limits; the statements checked against the paper independently;
  representation bridges proved; baseline committed.
- Stage 1: every internal result proved by the paper's argument; cited results isolated in the
  library `External`, with citations, stated in their sources' terms, and importing nothing from
  the paper's library.
- Stage 2: every cited result proved or derived from a library, or, when out of reach, a declared
  hypothesis named after its source; zero project axioms.
- Proof routes: `docs/paper_routes.tsv` committed and checked against the paper; the route check
  passes on the final commit, and every difference it records has its reason; every departure
  from the paper's proofs is necessary (Rules) and reported in its docstring, in the report's
  table of departures, in `formalization.yaml` and to the user; the formal proofs compared with
  the paper's independently of their provers.
- Verification: clean build; `scripts/Audit.lean` passes for every declaration; `Solution.lean`
  and `comparator.json` written, and Comparator accepts the solution; no assumption hidden in a
  parameter; every structure or class of hypotheses has an instance, or the reason it cannot have
  one yet is recorded.
- Cleanup: the build prints only the Challenge's `sorry` warnings; unused hypotheses removed, and
  those of paper results recorded; misleading names fixed; the route check passes as before.
- Documentation:
  - `REPORT.md` written, its findings checked against the source, and every departure from the
    paper's proofs listed in it; a conditional formalization says so in the README's first
    paragraph, in `formalization.yaml` and in the report, which lists what it assumes;
  - the report's literature section written from a dated search for the work before, alongside
    and after the paper (or, without network access, saying that no search could be made), with
    every source linked and its summary and date checked against it, and earlier formalizations
    cited; its "What's next" section with every simpler argument recorded during the work checked
    and either listed or set aside as wrong;
  - `README.md` rewritten for the current state, short, with status, results and findings in
    tables and a link to the report's departures (`audit-report.md`, Section 3); the repository
    description in step with it;
  - `CREDITS.md` reports the procedure, the agents and models, the elapsed time and the effort
    from the run log, round by round, and the README's credits sum it up with a link;
  - links up to date, tables valid; a draft's own notes deleted.
- Follow-up papers: `NEXT.md` written (`references/next-papers.md`), with each candidate above the
  bar, explored to the step where the paper's method stops, its claims marked as proved, checked
  or conjectured, and checked independently for novelty and substance, or with the statement that
  none meets the bar and what came closest; `NEXT.md` and `notes/next/` ignored by git and absent
  from every commit; the user told where they are.
- Packaging (unless declined): every file that adapts code from another project keeps that
  project's notice; `formalization.yaml` written; Palomar's metadata and source checks pass on a
  clean clone; the dependencies shared with Verso pinned at Verso's revisions for the toolchain;
  with the user's permission for each step, the repository published, CI passing, and the
  preflight reporting `status: pass` on the exact commit to submit; the user decides about
  submission and registration.
