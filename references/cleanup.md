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
   - Run `python3 scripts/strip_call_args.py <commit before the cleanup>` once. It deletes, at
     every call site, the arguments of the removed binders, and lists the call sites it cannot
     parse, such as an argument on the next line, for manual repair.
   - Rebuild, and fix what remains. Implicit arguments that only a removed hypothesis determined
     need a named argument at some call sites (`(x := x)`); a definition that matched on a
     membership proof (`if h : c ∈ s then … else …`) may now need a plain `if`.
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
- After moving or renaming modules, delete their old build outputs (`.olean`, `.ilean`, `.trace`
  and the hashes, under `.lake/build/lib/lean` and `.lake/build/ir`). Stale `.ilean` files make
  `scripts/linkify_docs.py` link to the old paths.
- Keep the generator of every generated Lean file in the repository (for example under
  `scripts/`), check that it reproduces the file byte for byte, and say in the README how to run
  it. Name template fragments that are not modules `*.lean.in`: Palomar rejects every `.lean`
  file that is not a module, used or not.
- Add `__pycache__/` to `.gitignore` when the repository contains Python scripts.
- Dead code, meaning helper lemmas nothing uses, can stay unless the user asks for a lean
  repository. If it goes, delete it in its own commit.
