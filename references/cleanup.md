# Cleanup: warnings, redundant hypotheses, names, stale files

The goal is a build that prints nothing but the intended `sorry` warnings of `Challenge.lean`.
Warnings do not affect correctness, but a clean build is easier to review, and unused hypotheses
often reveal redundant hypotheses of the paper. Cleanup changes how proofs are written, never which
argument they make: afterwards, every proof still follows the paper's (SKILL.md, Rules, "Faithful
proofs").

## Procedure

1. Capture the warnings: `lake build > build.log 2>&1`. Lake also prints the stored warnings of
   modules that are up to date. Classify them:
   `grep -o 'warning: [^:]*\.lean:[0-9]*:[0-9]*: .*' build.log | sort -u`.
2. Remove unused hypotheses (the "Variable name `h` is not explicitly referenced" warnings) in
   rounds, because removing a hypothesis can leave its caller's own hypotheses unused. A few
   rounds are usually enough. Each round:
   - Starts from a commit, with a fresh `build.log`.
   - `python3 <skill-dir>/scripts/strip_unused.py build.log` deletes each unused binder from its
     declaration; `--dry-run` only lists them. It skips variables that are not in a binder
     (`fun x`, `∃ x`), and lists them for you to fix by hand: write `_`, or restate (`∃ x, True`
     becomes `Nonempty …`).
   - `python3 <skill-dir>/scripts/strip_call_args.py` then deletes, at every call site, the
     arguments of the binders removed since the last commit, including named arguments. It lists
     the call sites that it cannot edit safely, for you to fix by hand (an argument on the next
     line, `@`, dot notation on a variable, a declaration passed as a value, a local name that may
     shadow it). It leaves the call sites that it cannot resolve at all to the rebuild. It refuses
     an older commit, and a second run against the same commit: either would also delete correct
     arguments.
   - Rebuild, and fix what remains. Implicit arguments that only a removed hypothesis determined
     need a named argument at some call sites (`(x := x)`), and a dependent `if h : …` whose `h`
     is no longer used becomes a plain `if`.
   - Ends with a commit.

   Delete `have` steps that only produced a removed argument; the linter does not flag them.
   Delete the binder rather than renaming it `_h`, unless the user wants the statement to match
   the paper character for character.
3. Fix the other warnings:
   - `haveI` or `letI` in proofs, with the hint "The goal is a proposition, so `let` is
     preferred": use `have` or `let`. The linter fires only when the goal is a proposition, and
     there the change is always safe, because proofs are irrelevant. Leave `letI` in statements
     alone.
   - "This simp argument is unused": delete it.
   - "automatically included section variable(s) unused": add `omit [Inst] in` before the
     theorem.
   - Deprecations: use the replacement that the warning names.
4. Rerun the checks: `lake build`, `scripts/Audit.lean`, the route check
   (`scripts/route_check.py check docs/paper_routes.tsv --accept docs/route_differences.tsv`)
   and `lake comparator`. If the documents already link to the code, also rerun
   `scripts/linkify_docs.py`, since line numbers move. A route difference that appears during the
   cleanup is a regression: undo the change that caused it.
5. Record, and commit:
   - Run `python3 <skill-dir>/scripts/stmt_diff.py <commit before the cleanup>`.
   - For each paper result that lost a hypothesis, the Lean statement is now more general than
     the paper's. Record the result, the hypothesis and why it is not needed. The audit lists
     them in the report's table of redundant hypotheses and in the README's summary.
   - A definition that lost an unused parameter changes how readers see it. If it is a notion of
     the paper, mention the change under "How the formalization reads the paper".
   - The Challenge statements keep the paper's hypotheses. An assumed result (SKILL.md, Rules)
     that no proof uses is not one of them: remove it everywhere, including the Challenge.
   - The commit message lists the removals.

## Simplifying proofs and merging duplicates

Shortening proofs, merging duplicate helper lemmas, moving shared facts into a common module and
splitting long files make a formalization easier to read, and are worth doing. They are also how
proofs drift away from the paper while no statement changes:

- When you merge two copies of a fact, keep the one whose proof follows the paper. A step that the
  paper justifies by a numbered result must still use that result, not the lemma underneath it. If
  the result is proved from a private lemma that you make public, prove the public lemma from the
  result instead (as a corollary after it), and keep the step's lemma private.
- A shorter proof of a paper result is acceptable only if it makes the same argument. Replacing
  the paper's argument with another one, even a better one, is a departure, and convenience is not
  a reason for one (SKILL.md, Rules). If the other argument is simpler for a reader of the paper,
  record it for the report's "What's next" section instead.
- Delete a `have` that nothing uses, even when it names a result that the paper cites. The route
  check then reports the difference, which is the truth about the proof. Then decide whether the
  proof should use that result after all.
- Work in rounds that end with the route check, and compare each round's report with the previous
  one: a route difference that a round introduced is undone in that round.

## Names and stale files

- Rename files and namespaces whose names mislead. A draft may call helper files `External.lean`
  even though they hold no cited results. Rename them, for example to `Auxiliary.lean`. Rename
  with a script that moves the files (`git mv`), rewrites the imports, rewrites qualified
  references to the declarations of the renamed namespace, and leaves the truly external names
  alone. Then fix the module docstrings by hand, and rebuild.
- Delete the draft's notes and checklists once `README.md` and `REPORT.md` replace them, in
  Phase 8. They remain in the history. Your own working notes (the inventory, the run log) are
  untracked and stay until the end.
- After moving or renaming modules, delete their old build outputs under `.lake/build`: stale
  `.ilean` files make `scripts/linkify_docs.py` link to the old paths.
- Keep the generator of every generated Lean file in the repository (for example under
  `scripts/`), check that it reproduces the file byte for byte, and say in the README how to run
  it. Name template fragments that are not modules `*.lean.in`: Palomar rejects every `.lean` file
  that is not a module, used or not.
- Add `__pycache__/` to `.gitignore` when the repository contains Python scripts.
- Dead code (helper lemmas nothing uses) can stay unless the user asks for a minimal
  repository. If you remove it, do so in its own commit.
