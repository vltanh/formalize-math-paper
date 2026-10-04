# The paper audit, `REPORT.md` and `README.md`

## Contents

1. Auditing the paper
2. `REPORT.md` structure
3. `README.md` structure
4. Style and mechanics

## 1. Auditing the paper

Collect findings throughout the formalization: proving each step is the most thorough reading a
paper gets. Then audit the paper separately, against its TeX source. For each kind of finding:

| Kind | How to find it | What to record |
| --- | --- | --- |
| Error | A step or claim that is false as written: a wrong inequality, constant or index range, a product that counts a factor twice, a theorem applied wrongly | Location and TeX line; why it is false (a counterexample or the computation); the correct version; whether the result still holds |
| Gap | A claim used without justification: "clearly", "it is easy to see", a missing case, a step that needs a condition the statement does not give | What is missing, and why it holds or does not; if the statement holds anyway, the corrected argument |
| Typo | A wrong cross-reference ("Theorem 1.2" for 1.3), a self-citation, a slip in a variable name | Location and correction |
| Missing hypothesis | A statement that is false without a condition that the paper leaves implicit | The condition, a counterexample without it, and where the formalization states it (a correction agreed with the user) |
| Redundant hypothesis | A hypothesis that a statement includes but its proof never uses: start from the hypotheses that the cleanup removed | The hypothesis, and whether the Lean statement drops it |
| Use of a cited result | Each citation used in a proof: are its hypotheses checked, and is it applied in the form it was proved in? | A verdict: correct, applied loosely but correctly, or stated or applied wrongly |

Verify every finding before you report it. Have someone other than the one who recorded it do this
(a separate agent if available, working from the TeX source and the inventory; otherwise a separate
pass of your own):

- Quote the TeX text. Do not report from memory of the PDF.
- Recompute every arithmetic claim, by script if needed: products and sums of constants,
  inequalities between explicit numbers, and thresholds that must hold for all large parameters.
- Decide whether the result still holds, and say so. Most errors in good papers are slips that
  leave the result intact. Overstating them destroys trust.
- A finding about the paper must hold for the paper's own statement. A step that fails only after a
  formalization choice, such as rounding to `ℕ`, is a reading, recorded in Section 6 of the report,
  not an error of the paper.
- Check every departure in Section 7 against the paper's proof in the TeX. The report must describe
  the paper's argument as the paper gives it, and the reason must be one of the three. A departure
  that its reason does not force is a proof to rewrite, not a line of the report.

Number the findings E1, E2, … in the order they occur in the paper. Group typos into one final
item. If you add or remove a finding later, renumber the findings, and update every reference to
them, in `REPORT.md` and in `README.md`.

Have someone other than its writer check the report's "What's next" section (Section 10) the same
way. That reader checks every summary of a later paper against that paper's abstract and
statements, and against its status (published, preprint, withdrawn or disputed); every claim that a
result has been extended or improved against the source that proves it; and every suggestion
against the literature and against the audit that it relies on. A suggestion that turns out to be
known is not a suggestion: it becomes a line of "Since the paper" if its source is later than the
paper, and otherwise part of the README's related work (item 7 of Section 3 below).

Later work that corrects the paper is a finding of the audit: an erratum, a later version that
fixes a slip, a counterexample to one of its results, or a gap that the audit missed. Add it to the
E-items, or update the E-item it concerns, citing the source, and carry it into the report's
Summary and the README's audit summary. Tell the user at once. If it bears on a result that the
project proved or assumed, also check the Lean statement, and any hypothesis it assumes, against
the paper and the source again.

## 2. `REPORT.md` structure

```markdown
# Audit of the paper and the formalization

Paper: <authors>, *<title>*, <arXiv id with version>. The audit was made against the arXiv
LaTeX source of that version. Section, result and equation numbers are the paper's.

Status of the formalization: <bullets: what is proved; where the cited results are proved; what is
assumed, if anything, which makes the result conditional; the build, sorry and axiom status, and
how the audit script checks it; Challenge and Comparator; whether any statement of the paper had to
change; whether every proof follows the paper's, and how many depart from it (Section 7)>

## 1. Summary
- **Errors.** … - **Gaps.** … - **Missing hypotheses.** … - **Redundant hypotheses.** …
- **Use of cited results.** …

## 2. Results from prior work and how the paper uses them
### Proved in `External/`
| Result | Where the paper uses it | Source | Theorem in `External/` |
### Assumed (a conditional formalization only)
| Result | Where the paper uses it | Source | Hypothesis in the formalization | What Lean lacks | Plan, if any |
<Check each hypothesis against its source as carefully as a statement: an assumption stated more
strongly than its source proves can make a theorem vacuous.>
### Standard facts used without citation
| Fact | Where | In the formalization (Mathlib name or local proof) |
### Does the paper use each cited result correctly?
| Cited result | Where | Verdict |
<A sentence listing the citations that only give context and are not used in proofs.>

## 3. Errors and gaps in the paper
**E1. <Location>.** <what is wrong, why, the correct version, whether the result still holds, how
the Lean handles it, and any later work that corrects it> … **En. Typos.** …

## 4. Missing hypotheses
<Conditions without which a statement is false, each with a counterexample, and where the
formalization states them. If a proof uses an unstated condition but the statement holds without
it, the proof has a gap (Section 3), and the statement stays as printed.>
| Where | Missing hypothesis | Counterexample without it | In the formalization |

## 5. Redundant hypotheses
<Hypotheses that the statements include but the proofs do not use; say whether the Lean
statements leave them out.> | Result | Hypothesis that is not needed | Lean |

## 6. How the formalization reads the paper
<Representation choices and precise readings of informal statements: probability spaces,
indexing, types of quantities, "max" as "for all", explicit constants, how cited results were
proved. If a statement of the paper had to be corrected, a second list: the corrections.>

## 7. Departures from the paper's proofs
<Every result whose formal proof does not follow the paper's argument, at any step, and why the
departure is necessary: one of the three reasons of SKILL.md's Rules (the paper's step is wrong or
has a gap that cannot be repaired along its lines; it needs mathematics that Lean lacks and the
project cannot build; it has no meaning in the formalization's representation). Keep this section
consistent with the docstrings, `formalization.yaml` and `docs/route_differences.tsv`. If there are
none, say that every proof follows the paper's.>
| Result | The paper's argument | The formalization's | Why it is necessary | E-item |

## 8. What each result depends on
<Generated from scripts/Audit.lean.> | Result | Lean | Results from prior work used |
<One sentence on the route check: every proof uses the results that the paper's proof cites,
except the differences recorded in docs/route_differences.tsv, each with its reason.>

## 9. Not formalized
<Everything in the paper that is not formalized: deductions that combine the paper with
unformalized prior work, surveys, remarks, experiments.>

## 10. What's next
<How the subject has developed since the paper, and how its results could be improved. Search
citation indexes and arXiv listings for the papers that cite it, for later results on the same
questions, and for errata and versions of the paper newer than the one formalized. Screen every
work you find by its abstract, and read the main statements, not only the titles, of those that
prove or claim something about the paper's results or questions. If there are many, keep the
closest ones and every correction or counterexample, and say how you chose them. Say when and where
you searched, and link every source. Without network access, say that no search could be made, and
write this section from the paper and the audit.>
### Since the paper
<What later work has proved or claims: extensions, generalizations, strengthenings, new proofs,
corrections, counterexamples. One sentence each, taken from the source, with a link and the
source's status: published (where), preprint, withdrawn or disputed. Report what a preprint, a
withdrawn or a disputed work claims as claimed, not as proved. A correction or a counterexample is
also a finding (Section 3). If the search found nothing, say so; earlier and concurrent work
belongs in the README's related work.>
### Open directions
<Ways to extend, generalize or strengthen the paper's results, drawn from: the paper's own remarks,
open questions and conjectures, and the hypotheses it says it needs only for its method (SKILL.md,
Phase 1); the audit (hypotheses that the proofs do not use, gaps whose repair gives more, steps
that hold more generally); the formalization (assumptions isolated as hypotheses, results proved
more generally than the paper states them); and the later work. For each: the statement to aim
for, what would have to be proved, and what stands in the way.>
### The formalization
<What would extend the formalization itself. Point to the assumed results of Section 2 and the
items of Section 9 instead of repeating them, and add what they lack: the generality to reach, and
the contributions to Mathlib or other libraries that would make the work feasible.>
```

## 3. `README.md` structure

The README is the project's front page. Keep it short: bullets rather than long paragraphs, and the
details left to `REPORT.md` and `CREDITS.md`.

1. Title, CI badge, and one paragraph on the paper and its main result, for a mathematician. If
   the formalization is conditional, this paragraph says so and names what it assumes.
2. What is proved: every result the paper proves; the cited results and where they are proved; the
   assumed results, if any, with a link to the report's table; the build, `sorry` and `axiom`
   status; the audit script and how to run it.
3. The main results: each Challenge theorem, linked, with a statement in plain language. For a
   well-known problem, compare the Challenge's formulation with the standard one.
4. Palomar (if packaged): the files, how to run `lake comparator`, the preflight workflow.
5. Audit summary: short bullets, using the report's E-numbers. Lead with errors, then gaps,
   missing and redundant hypotheses, and the use of cited results. Then the proofs: that they
   follow the paper's arguments, and every departure, with its reason.
6. Credits, in two or three bullets: who and what wrote the code, at whose request, and by which
   procedure, with a link to this skill's repository (for example: "first written by [AI system]
   as an uncompiled draft; [AI system] made it compile, checked the statements and wrote the
   audit"); whether a person has reviewed the proofs; and when it was made, with how many
   sub-agents. Then a link to `CREDITS.md` for the rest (its structure is in `credits.md`). No
   links to old drafts.
7. Related work: the history of the problem, the closest earlier and concurrent work, and the
   earlier formalizations of the paper or its result, with whether this work consulted them.
8. What's next: two or three sentences from the report's Section 10, with a link to it. If later
   work corrects the paper, start with that.
9. Building: `lake exe cache get`, `lake build`, the audit, the toolchain, how to regenerate
   generated files, and how to update the documentation's links.
10. Layout: a table of every module and the paper content it holds, and the `External/`
    directories.
11. GitHub configuration: what each workflow does and any settings it needs.
12. License.

## 4. Style and mechanics

- Write for mathematicians. Use the paper's notation in prose, and Lean names in code spans.
- The report describes only the paper and the current formalization. Leave out the history of the
  repair (which draft lemmas were false, what was renamed), and do not link to old drafts or pull
  requests. That history belongs in commit messages.
- Do not write down numbers that change, such as declaration counts, unless they are rechecked
  against the audit script's output after every change.
- Links: name Lean declarations in code spans, and let `scripts/linkify_docs.py` turn them into
  links to their lines. It reads the `.ilean` files, so run `lake build` first. Configure the
  documents and namespaces at the top of the script, and run it with `--check` in CI.
- Tables: in GitHub's Markdown, every `|` in a table row ends a cell, even inside backticks. Write
  `\|` for absolute values and cardinalities in tables (`` `\|S\| ≥ 2` ``).
  `scripts/check_md_tables.py --fix` escapes them, and without `--fix` it reports broken rows.
- Before publishing, render each document with GitHub's own renderer and read its tables. The
  renderer pads or cuts every row to the header's number of cells, so a broken row does not change
  the count: its text shows up in the wrong cell, or not at all.

  ```sh
  python3 -c 'import json,sys; print(json.dumps({"text": open(sys.argv[1]).read(), "mode": "markdown"}))' REPORT.md \
    | gh api -X POST markdown --input - > <scratch dir>/REPORT.html
  ```
