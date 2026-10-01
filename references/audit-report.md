# The paper audit, `REPORT.md` and `README.md`

## Contents

1. Auditing the paper
2. `REPORT.md` structure
3. `README.md` structure
4. Style and mechanics

## 1. Auditing the paper

Collect findings throughout the formalization, since proving each step is the most thorough
reading a paper gets. Then audit the paper separately, against its TeX source. For each kind of
finding:

| Kind | How to find it | What to record |
| --- | --- | --- |
| Error | A step or claim that is false as written: wrong inequality, wrong constant, wrong index range, a product that counts a factor twice, a misapplied theorem | Location and TeX line; why it is false (a counterexample or the computation); the correct version; whether the result survives |
| Gap | A claim used without justification: "clearly", "it is easy to see", an omitted case, an implicit condition | What is missing and why it holds, or does not |
| Typo | Wrong cross-reference ("Theorem 1.2" for 1.3), self-citation, a variable name slip | Location and correction |
| Missing hypothesis | A statement whose proof needs a condition the statement does not have | The condition, and where the formalization states it |
| Redundant hypothesis | A statement hypothesis that the proof never uses: start from the hypotheses that the cleanup removed | The hypothesis, and whether the Lean statement drops it |
| Use of a cited result | Each citation used in a proof: are its hypotheses checked, is it applied in the form it was proved in? | A verdict: correct, applied loosely but correctly, or misstated or misapplied |

Verify every finding before reporting it:

- Quote the TeX text. Do not report from memory of the PDF.
- Recompute every arithmetic claim, by script if needed: products and sums of constants,
  inequalities between explicit numbers, and thresholds that must hold for all large parameters.
- Decide whether the result survives, and say so. Most errors in good papers are slips that
  leave the result intact. Overstating them destroys trust.
- A finding about the paper must hold for the paper's own statement. A step that only fails
  after a formalization choice, such as rounding to `ℕ`, is a reading, recorded in Section 6 of
  the report, not an error of the paper.

Number the findings E1, E2, … in the order they occur in the paper. Group typos into one final
item. If you insert a finding later, renumber, and update every reference in `README.md`.

## 2. `REPORT.md` structure

```markdown
# Audit of the paper and the formalization

Paper: <authors>, *<title>*, <arXiv id with version>. The audit was made against the arXiv
LaTeX source of that version. Section, result and equation numbers are the paper's.

Status of the formalization: <bullets: what is proved; cited results proved where; build, sorry
and axiom status and how the audit script checks it; Challenge and Comparator; whether any
statement of the paper had to change>

## 1. Summary
- **Errors.** … - **Gaps.** … - **Missing hypotheses.** … - **Redundant hypotheses.** …
- **Use of cited results.** …

## 2. Results from prior work and how the paper uses them
### Proved in `External/`
| Result | Where the paper uses it | Source | Theorem in `External/` |
### Standard facts used without citation
| Fact | Where | In the formalization (Mathlib name or local proof) |
### Does the paper use each cited result correctly?
| Cited result | Where | Verdict |
<A sentence listing citations that only give context and are not used in proofs.>

## 3. Errors and gaps in the paper
**E1. <Location>.** <what is wrong, why, the correct version, whether the result survives, how
the Lean handles it> … **En. Typos.** …

## 4. Missing hypotheses
<Hypotheses that the arguments need but the statements lack.> | Where | Missing hypothesis | In the formalization |

## 5. Redundant hypotheses
<Hypotheses that the statements include but the proofs do not use; say whether the Lean
statements omit them.> | Result | Hypothesis that is not needed | Lean |

## 6. How the formalization reads the paper
<Representation choices and precise readings of informal statements: probability spaces,
indexing, types of quantities, "max" as "for all", explicit constants, how cited results were
proved. If a paper statement had to be corrected, a second list: the corrections.>

## 7. What each result depends on
<Generated from scripts/Audit.lean.> | Result | Lean | Results from prior work used |

## 8. Not formalized
<Everything in the paper that is not formalized: deductions that combine the paper with
unformalized prior work, surveys, remarks, experiments.>
```

## 3. `README.md` structure

1. Title, CI badge, and one paragraph on the paper and its main result, for a mathematician.
2. What is proved: every result the paper proves; the cited results and where they are proved;
   build, `sorry` and `axiom` status; the audit script and how to run it.
3. The main results: each Challenge theorem, linked, with a plain-language statement.
4. Palomar (if packaged): the files, how to run `lake comparator`, the preflight workflow.
5. Audit summary: short bullets, using the report's E-numbers. Lead with errors, then gaps,
   missing and redundant hypotheses, and the use of cited results.
6. Credits: who and what wrote the code. For example: "first written by [AI system] as an
   uncompiled draft; [AI system] made it compile, checked the statements and wrote the audit".
   No links to superseded drafts.
7. Building: `lake exe cache get`, `lake build`, the audit, the toolchain, and how to update the
   documentation's links.
8. Layout: a table of every module and the paper content it holds, and the `External/`
   directories.
9. GitHub configuration: what each workflow does and any settings it needs.
10. License.

## 4. Style and mechanics

- Write for mathematicians. Use the paper's notation in prose, and Lean names in code spans.
- The report describes the paper and the current formalization only. Do not include a history of
  the repair (which draft lemmas were false, what was renamed), and do not link to superseded
  drafts or pull requests. That belongs in commit messages.
- Do not hard-code numbers that change, such as declaration counts, unless the audit script's
  output is rechecked after every change.
- Links: name Lean declarations in code spans, and let `scripts/linkify_docs.py` turn them into
  links to their lines. It reads the `.ilean` files, so run `lake build` first. Configure the
  documents and namespaces at the top of the script, and run it with `--check` in CI.
- Tables: in GitHub's Markdown, every `|` in a table row ends a cell, even inside backticks.
  Write `\|` for absolute values and cardinalities in tables (`` `\|S\| ≥ 2` ``).
  `scripts/check_md_tables.py --fix` escapes them, and without `--fix` it reports broken rows.
- Before publishing, render each document with GitHub's own renderer and check that every table
  has the same number of cells in every row:

  ```sh
  python3 -c 'import json,sys; print(json.dumps({"text": open(sys.argv[1]).read(), "mode": "markdown"}))' REPORT.md \
    | gh api -X POST markdown --input - > /tmp/REPORT.html
  ```
