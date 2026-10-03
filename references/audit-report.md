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
| Gap | A claim used without justification: "clearly", "it is easy to see", an omitted case, a step that needs a condition the statement does not give | What is missing and why it holds, or does not; if the statement holds anyway, the corrected argument |
| Typo | Wrong cross-reference ("Theorem 1.2" for 1.3), self-citation, a variable name slip | Location and correction |
| Missing hypothesis | A statement that is false without a condition that the paper leaves implicit | The condition, a counterexample without it, and where the formalization states it (a correction agreed with the user) |
| Redundant hypothesis | A statement hypothesis that the proof never uses: start from the hypotheses that the cleanup removed | The hypothesis, and whether the Lean statement drops it |
| Use of a cited result | Each citation used in a proof: are its hypotheses checked, is it applied in the form it was proved in? | A verdict: correct, applied loosely but correctly, or misstated or misapplied |

Verify every finding before reporting it, by a reader other than the one who recorded it (a
separate agent if available, working from the TeX source and the inventory; otherwise a separate
pass):

- Quote the TeX text. Do not report from memory of the PDF.
- Recompute every arithmetic claim, by script if needed: products and sums of constants,
  inequalities between explicit numbers, and thresholds that must hold for all large parameters.
- Decide whether the result survives, and say so. Most errors in good papers are slips that
  leave the result intact. Overstating them destroys trust.
- A finding about the paper must hold for the paper's own statement. A step that only fails
  after a formalization choice, such as rounding to `ℕ`, is a reading, recorded in Section 6 of
  the report, not an error of the paper.
- Check every departure of Section 7 against the paper's proof in the TeX: the paper's argument
  must be described as the paper gives it, and the reason must be one of the three. A departure
  that the reason does not force is a proof to rewrite, not a line of the report.

Number the findings E1, E2, … in the order they occur in the paper. Group typos into one final
item. If you insert a finding later, renumber, and update every reference in `README.md`.

Check the report's "What's next" section (Section 10) the same way: every summary of a later
paper against that paper's abstract and statements, every claim that a result has been extended
or improved against the source that proves it, and every suggestion against the literature (a
suggestion that turns out to be known becomes a line of "Since the paper", or of the paper's own
background) and against the audit that it relies on.

## 2. `REPORT.md` structure

```markdown
# Audit of the paper and the formalization

Paper: <authors>, *<title>*, <arXiv id with version>. The audit was made against the arXiv
LaTeX source of that version. Section, result and equation numbers are the paper's.

Status of the formalization: <bullets: what is proved; cited results proved where; what is
assumed, if anything, so that the result is conditional; build, sorry and axiom status and how
the audit script checks it; Challenge and Comparator; whether any statement of the paper had to
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
<A sentence listing citations that only give context and are not used in proofs.>

## 3. Errors and gaps in the paper
**E1. <Location>.** <what is wrong, why, the correct version, whether the result survives, how
the Lean handles it> … **En. Typos.** …

## 4. Missing hypotheses
<Conditions without which a statement is false, each with a counterexample, and where the
formalization states them. A proof that uses an unstated condition while the statement holds
without it has a gap (Section 3), and its statement stays as printed.>
| Where | Missing hypothesis | Counterexample without it | In the formalization |

## 5. Redundant hypotheses
<Hypotheses that the statements include but the proofs do not use; say whether the Lean
statements omit them.> | Result | Hypothesis that is not needed | Lean |

## 6. How the formalization reads the paper
<Representation choices and precise readings of informal statements: probability spaces,
indexing, types of quantities, "max" as "for all", explicit constants, how cited results were
proved. If a paper statement had to be corrected, a second list: the corrections.>

## 7. Departures from the paper's proofs
<Every result whose formal proof does not follow the paper's argument, at any step, and why the
departure is necessary: one of the three reasons of SKILL.md's Rules (the paper's step is wrong or
has a gap that cannot be repaired along its lines; it needs mathematics that Lean lacks and the
project cannot build; it has no meaning in the formalization's representation). Agree with the
docstrings, `formalization.yaml` and `docs/route_differences.tsv`. If there is none, say that
every proof follows the paper's.>
| Result | The paper's argument | The formalization's | Why it is necessary | E-item |

## 8. What each result depends on
<Generated from scripts/Audit.lean.> | Result | Lean | Results from prior work used |
<One sentence on the route check: every proof uses the results that the paper's proof cites,
except the differences recorded in docs/route_differences.tsv, each with its reason.>

## 9. Not formalized
<Everything in the paper that is not formalized: deductions that combine the paper with
unformalized prior work, surveys, remarks, experiments.>

## 10. What's next
<How the subject has moved since the paper, and how its results could be improved. Say when and
where the search for later work was made (citation indexes, arXiv), and link every source.>
### Since the paper
<What later work has proved: extensions, generalizations, strengthenings, new proofs,
corrections, counterexamples. One sentence each, taken from the source, with a link. If the
search found nothing, say so, and name the closest earlier or concurrent work.>
### Extensions, generalizations and strengthenings
<Directions from the paper's remarks and open questions, from the audit (unused hypotheses, gaps
whose repair gives more, steps that hold more generally), from the formalization, and from the
later work. For each: the statement to aim for, what would have to be proved, and what stands in
the way. Keep these apart from what is already proved.>
### The formalization
<What would extend the formalization itself: the assumed results to prove, the generality to
reach, and the contributions to Mathlib or other libraries that would make them feasible.>
```

## 3. `README.md` structure

1. Title, CI badge, and one paragraph on the paper and its main result, for a mathematician. If
   the formalization is conditional, this paragraph says so and names what it assumes.
2. What is proved: every result the paper proves; the cited results and where they are proved;
   the assumed results, if any, with a link to the report's table; build, `sorry` and `axiom`
   status; the audit script and how to run it.
3. The main results: each Challenge theorem, linked, with a plain-language statement. For a
   well-known problem, compare the Challenge's formulation with the standard one.
4. Palomar (if packaged): the files, how to run `lake comparator`, the preflight workflow.
5. Audit summary: short bullets, using the report's E-numbers. Lead with errors, then gaps,
   missing and redundant hypotheses, and the use of cited results. Then the proofs: that they
   follow the paper's arguments, and every departure, with its reason.
6. Credits: who and what wrote the code, and how it was made. For example: "first written by
   [AI system] as an uncompiled draft; [AI system] made it compile, checked the statements and
   wrote the audit". No links to superseded drafts. Report the run log's figures:
   - the procedure, with a link to this skill's repository and its version or commit;
   - the agent and harness, and the model(s), with their versions;
   - the number of sub-agents, how many ran at once at most, and what each kind did;
   - the elapsed time from the start to the audited formalization, with dates and time zone, and
     the total working time of the sub-agents;
   - tool calls and tokens, when the platform records them, with output, input and cache reads
     counted separately: they differ by orders of magnitude.
7. Related work: the history of the problem, and the earlier formalizations of the paper or its
   result, with whether this work consulted them.
8. What's next: two or three sentences from the report's Section 10, with a link to it.
9. Building: `lake exe cache get`, `lake build`, the audit, the toolchain, how to regenerate
   generated files, and how to update the documentation's links.
10. Layout: a table of every module and the paper content it holds, and the `External/`
    directories.
11. GitHub configuration: what each workflow does and any settings it needs.
12. License.

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
- Before publishing, render each document with GitHub's own renderer and read its tables. The
  renderer pads or truncates every row to the header's number of cells, so a broken row does not
  change the count: it shows as text in the wrong cell, or missing.

  ```sh
  python3 -c 'import json,sys; print(json.dumps({"text": open(sys.argv[1]).read(), "mode": "markdown"}))' REPORT.md \
    | gh api -X POST markdown --input - > <scratch dir>/REPORT.html
  ```
