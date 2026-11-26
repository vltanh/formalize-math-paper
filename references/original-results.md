# Original results

The mathematics to formalize is sometimes the user's own: a proof they found, a manuscript not yet
published, an argument from a discussion or a pull request. No published paper stands behind it.
The formalization is then the first complete check of the argument, and often its record: there is
no paper to audit, and no printed argument that the proofs must follow.

## Contents

1. What stays
2. What changes
3. A paper written with the formalization
4. A paper's formalization with results of its own

## 1. What stays

Everything that makes the result checkable and reusable:

- the layout (`lean-project.md`), with a name for the result (`ResultName`) wherever the references
  write `PaperName`;
- statements first, checked independently against the user's text (SKILL.md, Principles), and
  committed as the baseline;
- the cited results, stated in their sources' terms and proved, and the theory that Lean lacks,
  built where `separate-packages.md` puts it (SKILL.md, Rules, "Mathematics that Lean lacks");
- verification: the axiom audit, the questions that a passing build does not answer
  (`checklists.md`, Section 2), the Solution and Comparator;
- cleanup, `CREDITS.md` and the run log, the permissions, and Palomar packaging.

## 2. What changes

- Statements. State what the user claims. When the proof gives more (a hypothesis that it never
  uses, a stronger conclusion, a wider range), state and prove the stronger form, and tell the user.
  A claim that is false is reported at once, with its counterexample, as for a paper (SKILL.md,
  Rules, "Statements").
- Proofs. The user's argument is where the proofs start, not a standard that they must keep to:
  prefer the shorter or more general proof, whoever found it. A gap in the argument is repaired in
  Lean and told to the user. There are no departures to report, so there are no route files in
  `docs/`, no route check in CI and no table of departures.
- Documents. They present the work as an original result, never as an audit of a paper: there is no
  `REPORT.md` with findings. The README says what is proved, with the exact statements, how to check
  it, the prior work and the credits (`audit-report.md`, Section 3, adapted). `docs/ResultName/`
  holds what a reader needs beyond the README:
  - the definitions and statements, explained;
  - an outline of the proof;
  - the prior work, written and checked like the report's literature section (the report's
    Section 10, in `audit-report.md`, Section 2);
  - the paper, if one is written (Section 3);
  - `CREDITS.md`.
- Follow-up papers (SKILL.md, Phase 8) only if the user asks for them.
- Prior work. Search for the result itself at the start (SKILL.md, Phase 0), as the report's
  literature section would (Phase 8), before calling it new. If it is already published, tell the
  user at once: the work is then a new proof of a known result, and the documents say so.
- Palomar. In `formalization.yaml`, one source declares the original proof (`type: original-proof`,
  `relationship: other`), and every other source is `background` or `other`. A new proof of a
  published result is not an original result for Palomar: that publication is the source, with
  `relationship: independently-proves` (`palomar.md`, Section 4). `fidelity` records how the formal
  statements read the user's text, and any statement made stronger.
- Credit. Whoever found the argument is credited: people as authors, AI systems in `CREDITS.md`
  and in `automation`, never as authors (SKILL.md, Rules, "Permissions and credit").
- Completion. The gates of `checklists.md`, Section 4, apply, except those about the paper's proofs
  (routes and departures), the report's findings and the follow-up papers.

## 3. A paper written with the formalization

When the user writes a paper about the result, or asks for one, the paper and the Lean say the same
thing:

- every numbered statement of the paper has one Lean theorem with the same content, including the
  parts that are easy to drop ("if and only if", "with equality exactly when");
- the objects are defined in Lean as the paper defines them, and other forms are lemmas;
- the paper states the generality that the Lean proves.

There is no list of differences between the two. When they differ, resolve the difference at its
source, and keep the better version in both: the more general or stronger statement, the shorter
proof. Facts that the paper only quotes from the literature are its scope, not differences.

## 4. A paper's formalization with results of its own

A project that formalizes a paper and also proves results beyond it keeps the two apart. The paper's
library, Challenge and documents follow the workflow for the paper, and stay about the paper. The
additions are original results: they have a library of their own, which may import the paper's
library, and their own Challenge, Solution and documents, laid out as another paper of the
repository (`multi-paper.md`, Sections 2 and 9). A theorem that only combines results of papers
formalized in the repository is not an addition: `multi-paper.md`, Section 4, places it. What both
use goes in a library that they share, and the paper's library never imports the additions. Each is
a Palomar submission of its own: the paper's `formalizes` the paper, and the additions' declares the
original proof, with the paper as `background` (`palomar.md`, Section 4).

Whether the additions are published, and where, is the user's decision. Until then they stay out of
the paper's public files, which do not mention them.
