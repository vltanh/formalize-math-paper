# Cleanup: warnings, redundant hypotheses, names, stale files

The goal is a build that prints nothing but the deliberate `sorry` warnings of `Challenge.lean`.
Warnings are harmless to correctness, but a clean build is easier to review, and unused
hypotheses often reveal redundant hypotheses of the paper. Cleanup changes how proofs are
written, never which argument they make: every proof still follows the paper's afterwards
(SKILL.md, Rules, "Faithful proofs").

## Procedure

1. Capture the warnings: `lake build > build.log 2>&1`. Lake replays the warnings of up-to-date
   modules. Classify them:
   `grep -o 'warning: [^:]*\.lean:[0-9]*:[0-9]*: .*' build.log | sort -u`.
2. Remove unused hypotheses (the "Variable name `h` is not explicitly referenced" warnings), in
   rounds, because removing a hypothesis can leave its caller's own hypotheses unused. A few
   rounds usually suffice. Each round:
   - Starts from a commit, with a fresh `build.log`.
   - `python3 <skill-dir>/scripts/strip_unused.py build.log` deletes each unused binder from its
     declaration; `--dry-run` only lists them. It skips variables that are not in a binder
     (`fun x`, `∃ x`) and lists them for manual repair: write `_`, or restate (`∃ x, True`
     becomes `Nonempty …`).
   - `python3 <skill-dir>/scripts/strip_call_args.py` then deletes, at every call site, the
     arguments of the binders removed since the last commit, named arguments included. It lists
     the call sites that it cannot edit safely for manual repair (an argument on the next line,
     `@`, dot notation on a variable, a declaration passed as a value, a local name that may
     shadow it), and leaves those it cannot resolve at all to the rebuild. It refuses an older
     commit, and a second run against the same one, either of which would delete further,
     correct arguments.
   - Rebuild, and fix what remains. Implicit arguments that only a removed hypothesis determined
     need a named argument at some call sites (`(x := x)`), and a dependent `if h : …` whose `h`
     is no longer used becomes a plain `if`.
   - Ends with a commit.

   Delete `have` steps that only produced a removed argument; the linter does not flag them.
   Delete the binder rather than renaming it `_h`, unless the user wants the statement to match
   the paper character for character.
3. Fix the other warnings:
   - `haveI` or `letI` in proofs, with the hint "The goal is a proposition, so `let` is
     preferred": use `have` or `let`. The linter fires only when the goal is a proposition, where
     the change is always safe, since proofs are irrelevant. Leave `letI` in statements alone.
   - "This simp argument is unused": delete it.
   - "automatically included section variable(s) unused": add `omit [Inst] in` before the
     theorem.
   - Deprecations: use the replacement that the warning names.
4. Rerun the checks: `lake build`, `scripts/Audit.lean`, the route check
   (`scripts/route_check.py check docs/paper_routes.tsv --accept docs/route_differences.tsv`)
   and `lake comparator`, and, if documents already link to the code, `scripts/linkify_docs.py`,
   since line numbers move. A route difference that appears during the cleanup is a regression:
   undo the change that caused it.
5. Record, and commit:
   - Run `python3 <skill-dir>/scripts/stmt_diff.py <commit before the cleanup>`.
   - For each paper result that lost a hypothesis, the Lean statement is now more general than
     the paper's. Record the result, the hypothesis and why it is not needed. The audit lists
     them in the report's redundant-hypotheses table and the README summary.
   - Definitions that lost an unused parameter change how readers see them. Mention it under
     "How the formalization reads the paper" if they are paper notions.
   - The Challenge statements keep the paper's hypotheses. An assumed result (SKILL.md, Rules)
     that no proof uses is not one of them: remove it everywhere, the Challenge included.
   - The commit message lists the removals.

## Simplifying proofs and merging duplicates

Shortening proofs, merging duplicate helper lemmas, moving shared facts into a common module and
splitting long files make a formalization easier to read, and are worth doing. They are also how
proofs drift from the paper without any statement changing:

- When two copies of a fact are merged, keep the one whose proof follows the paper. A step that
  the paper justifies by a numbered result must still go through that result, not through the
  lemma underneath it: if the result is proved from a private lemma that you make public, prove
  the public lemma from the result instead (a corollary after it), and keep the step's lemma
  private.
- A shorter proof of a paper result is acceptable only if it makes the same argument. Replacing
  the paper's argument by another one, even a better one, is a departure, and convenience is not
  a reason for one (SKILL.md, Rules).
- Delete a `have` that nothing uses, even when it names a result that the paper cites: the route
  check then reports the difference, which is the truth about the proof. Then decide whether the
  proof should use that result after all.
- Work in rounds that end with the route check, and compare each round's report with the
  previous one: a route difference that a round introduced is undone in that round.

## Names and stale files

- Rename files and namespaces whose names mislead. A draft may call helper files `External.lean`
  even though they hold no cited results. Rename them, for example to `Auxiliary.lean`. Rename
  with a script that moves the files (`git mv`), rewrites the imports, rewrites qualified
  references to the declarations of the renamed namespace, and leaves the genuinely external
  names alone. Then fix the module docstrings by hand, and rebuild.
- Delete the draft's notes and checklists once `README.md` and `REPORT.md` supersede them, in
  Phase 8. They remain in the history. Your own working notes (the inventory, the run log) are
  untracked and stay until the end.
- After moving or renaming modules, delete their old build outputs under `.lake/build`: stale
  `.ilean` files make `scripts/linkify_docs.py` link to the old paths.
- Keep the generator of every generated Lean file in the repository (for example under
  `scripts/`), check that it reproduces the file byte for byte, and say in the README how to run
  it. Name template fragments that are not modules `*.lean.in`: Palomar rejects every `.lean`
  file that is not a module, used or not.
- Add `__pycache__/` to `.gitignore` when the repository contains Python scripts.
- Dead code, meaning helper lemmas nothing uses, can stay unless the user asks for a lean
  repository. If it goes, delete it in its own commit.
