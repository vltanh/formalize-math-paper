# Cleanup: warnings, redundant hypotheses, names, stale files

The goal is a build that prints nothing but the deliberate `sorry` warnings of `Challenge.lean`.
Warnings are harmless to correctness, but a clean build is easier to review, and unused
hypotheses often reveal redundant hypotheses of the paper.

## Procedure

1. Capture the warnings: `lake build > build.log 2>&1`. Lake replays the warnings of up-to-date
   modules. Classify them:
   `grep -o 'warning: [^:]*\.lean:[0-9]*:[0-9]*: .*' build.log | sort -u`.
2. Remove unused hypotheses (the "Variable name `h` is not explicitly referenced" warnings):
   - `python3 scripts/strip_unused.py build.log` deletes each unused binder from its
     declaration; `--dry-run` only lists them. It skips variables that are not in a binder
     (`fun x`, `∃ x`) and lists them for manual repair: write `_`, or restate (`∃ x, True`
     becomes `Nonempty …`).
   - Rebuild. The errors now point at call sites that still pass the removed arguments; delete
     those arguments. Implicit arguments that were inferred from a removed hypothesis may need a
     named argument (`(x := x)`).
   - Repeat: removing a hypothesis can leave its caller's own hypotheses unused. A few rounds
     usually suffice.
   - Delete `have` steps that only produced a removed argument. The linter does not flag them.
   - Delete the binder rather than renaming it `_h`, unless the user wants the statement to
     match the paper character for character.
3. Fix the other warnings:
   - `letI` in proofs, with the hint "The goal is a proposition, so `let` is preferred": use
     `let`. This is always safe when the class is a `Prop`, and usually safe otherwise. Leave
     `letI` in statements alone.
   - "This simp argument is unused": delete it.
   - "automatically included section variable(s) unused": add `omit [Inst] in` before the
     theorem.
   - Deprecations: use the replacement that the warning names.
4. Rerun the checks: `lake build`, `scripts/Audit.lean` and `lake comparator`, and, if
   documents already link to the code, `scripts/linkify_docs.py`, since line numbers move.
5. Record, and commit:
   - Run `python3 scripts/stmt_diff.py <commit before cleanup>`.
   - For each paper result that lost a hypothesis, the Lean statement is now more general than
     the paper's. Record the result, the hypothesis and why it is not needed. The audit lists
     them in the report's redundant-hypotheses table and the README summary.
   - Definitions that lost an unused parameter change how readers see them. Mention it under
     "How the formalization reads the paper" if they are paper notions.
   - The Challenge statements stay exactly the paper's.
   - The commit message lists the removals.

## Names and stale files

- Rename files and namespaces whose names mislead. A draft may call helper files `External.lean`
  even though they hold no cited results. Rename them, for example to `Auxiliary.lean`. Rename
  with a script that moves the files (`git mv`), rewrites the imports, rewrites qualified
  references to the declarations of the renamed namespace, and leaves the genuinely external
  names alone. Then fix the module docstrings by hand, and rebuild.
- Delete the draft's notes and checklists once `README.md` and `REPORT.md` supersede them. They
  remain in the history.
- Dead code, meaning helper lemmas nothing uses, can stay unless the user asks for a lean
  repository. If it goes, delete it in its own commit.
