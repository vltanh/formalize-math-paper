# Proving in parallel with subagents

Once every statement elaborates, the remaining `sorry`s can be split among parallel subagents.
Statements are fixed and each module's `.olean` exists, so an agent can work on its files
against the compiled interfaces of the files they import, without waiting for upstream proofs.

## Before spawning

1. Every statement elaborates, and the statement-first commit exists. Statement diffs are measured
   against it.
2. Run a full `lake build`, so that every `.olean` exists. Agents check their files with
   `lake env lean` against those outputs.
3. Count the `sorry`s per file (`grep -cw sorry`).

## Partitioning

- Partition by files along the dependency order. An agent owns whole files: never give two agents
  the same file.
- Aim for about 20–40 `sorry`s per agent. Group small files of one section together. Give a very
  large file its own agent, or split it into modules first.
- Downstream agents can start at once. They rely on upstream statements, which are already
  compiled, and not on upstream proofs.
- Spawn all agents in one message, in the background, so they run concurrently.

## Agent brief

Copy this, filling in the brackets:

```text
You are repairing part of a Lean 4 formalization of [paper] in [repository path].
Statements already elaborate; proofs marked `sorry` remain.

Your files (only edit these): [list, with sorry counts]
Check a file with: [lake env lean -D... <file>]   (upstream .oleans are built)

Goal: replace every `sorry` in your files with a proof. No `sorry`, `admit`, `axiom`,
`native_decide`, `implemented_by` or raised heartbeats in the result.

Statements: keep every existing statement exactly as it is. The paper's results, listed here,
must never change: [names]. If a helper lemma is false as stated, find a concrete counterexample
(checked in Lean when possible), add the minimal hypothesis, fix its callers in your files, and
report it. Never change a statement merely to make a proof easier.

Upstream lemmas you may use as stated (some are still `sorry` and are being proved by other
agents): [list or "anything in imported modules"]. If one of them looks false, report it and do
not rely on it.

New helpers: make them `private`, or prefix their names with [file-specific prefix], so they
cannot clash with other agents' helpers.

Builds: do not run a full `lake build`. If you must rebuild an upstream module, build only that
module. If another build is running you may see "object file … does not exist": wait and retry,
and do not edit around it.

Report: sorries remaining per file; every statement change with its counterexample; every
upstream lemma you found false; new public helpers; anything the coordinator must relay.
```

## While agents run

- When an agent reports a signature change that affects another agent's files, relay it to that
  agent at once (with `SendMessage`, using its id). Include the new signature and how to update
  the call.
- When an agent reports a false upstream lemma, tell the owner of that file. Fixing it is that
  owner's job.
- Use the waiting time for work that does not touch the Lean files: the paper audit, document
  drafts, Palomar files.

## Integrating

1. Run a full `lake build` and fix integration errors. They usually come from signature changes
   that did not reach a caller, or from stale `.olean`s.
2. Check the axioms of the main theorems (`#print axioms`), then run the full
   `scripts/Audit.lean`.
3. Run `python3 scripts/stmt_diff.py <statement-first commit>`. It lists every declaration whose
   statement or definition body changed. Compare the list with the agents' reports.
   - An unreported change is either a false statement that was fixed silently (find the
     counterexample) or an unjustified weakening (revert it).
   - A paper result must not appear in the list.
4. Commit. The message lists every helper lemma found false, the hypothesis added, and why.
   Commit messages are where the repair's history belongs; the report describes only the final
   formalization.

## Handling false statements

- **Helper lemma false.** Add the minimal hypothesis that makes it true and is available at every
  call site. The usual suspects are truncated subtraction or division on `ℕ`, missing positivity
  or nonnegativity, empty sets or zero sizes, and boundary indices.
- **A definition that does not match its lemmas.** Sometimes the lemmas describe the intended
  object and the definition is wrong. Redefine it as exactly what the lemmas describe, and check
  that the definition still matches the paper.
- **Paper result false as stated.** Stop and tell the user, with the counterexample and the TeX
  location. With their agreement, formalize the minimal correct statement and record it in the
  report as an error, under "How the formalization reads the paper" and in
  `formalization.yaml`'s `fidelity`.
