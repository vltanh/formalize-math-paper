# Lean project setup and build discipline

## Contents

1. Versions
2. `lakefile.toml`
3. The module system
4. Checking files and building
5. Common errors when repairing a draft

## 1. Versions

Unless the user pins a version, use the newest Lean release or release candidate that Palomar
accepts (at least the minimum in PalomarSubmission's `toolchains.json`), and pin Mathlib to its
release tag for that toolchain rather than to `master`. Palomar renders the Challenge with the
release of the documentation tool Verso for the same toolchain, and the packages that Verso and
Mathlib share must then be pinned at the same revisions. Mathlib's release tag satisfies this;
later `master` commits soon stop doing so (`palomar.md`, Section 1). The project's
`lean-toolchain` must equal the pinned Mathlib commit's exactly, release-candidate suffix
included.

```sh
lake +leanprover/lean4:<version> new PaperName math   # then set Mathlib's rev to the release tag
lake update                                           # writes lake-manifest.json with the exact Mathlib commit
cat .lake/packages/mathlib/lean-toolchain             # must equal ./lean-toolchain
lake exe cache get                                    # download Mathlib's compiled files
```

Commit `lean-toolchain`, `lakefile.toml` and `lake-manifest.json`, and put `/.lake` in
`.gitignore`, with `/notes` if the working notes live in the repository directory and
`__pycache__/` if it holds Python scripts. Never commit `.olean`, `.ilean` or other build
outputs.

## 2. `lakefile.toml`

```toml
name = "PaperName"
version = "0.1.0"
keywords = ["math"]
defaultTargets = ["PaperName", "Challenge", "Solution"]

[leanOptions]
pp.unicode.fun = true
autoImplicit = false          # catches typos that would otherwise become implicit variables
maxSynthPendingDepth = 3      # Mathlib's own setting

[[require]]
name = "mathlib"
scope = "leanprover-community"
rev = "v4.35.0-rc3"           # for example: Mathlib's release tag for lean-toolchain

[[lean_lib]]
name = "PaperName"
globs = ["PaperName.+"]       # builds every module under PaperName/; drop it if PaperName.lean imports them all

[[lean_lib]]
name = "Challenge"

[[lean_lib]]
name = "Solution"
```

Create `Challenge.lean` and `Solution.lean` with the project, as modules that are empty except for
their imports, so that `lake build` works from the start; Phase 3 fills in the Challenge and
Phase 6 the Solution. `Solution.lean` can import the whole development and serve as the library's
entry point. Then no separate umbrella file `PaperName.lean` is needed, and the `globs` line keeps
every module in the build.

## 3. The module system

Palomar requires every `.lean` file, scripts included, to begin with `module` (only comments may
precede it) and to have at most 10,000 lines. A module file looks like this:

```lean
module

public import Mathlib.Analysis.SpecialFunctions.Log.Basic
public import PaperName.Preliminaries

/-! # Module title

Module documentation comes after `module` and the imports. -/

@[expose] public section

namespace PaperName
-- definitions and theorems
end PaperName
```

- `public import` makes an import part of the module's public interface. Statements that mention
  imported declarations need it.
- `@[expose] public section` exports the declarations and the bodies of definitions. Downstream
  files need the bodies to unfold definitions.
- A `private` declaration cannot appear in the statement of a public one. Make it public, or keep
  it out of statements.
- Proofs of imported theorems are not visible with a plain `import`. Scripts that inspect proofs,
  such as dependency analysis, need `import all M` for each module `M`. `collectAxioms` works
  without `import all`, because Lean records the axioms of every exported declaration when it
  compiles a module.
- Scripts are modules too. Write meta code like this:

  ```lean
  module
  public meta import Lean.Elab.Command
  import all PaperName.Main

  open Lean Elab Command
  meta def helper : Nat := 0
  elab "#mycommand" : command => do logInfo m!"{helper}"
  #mycommand
  ```

- To convert a non-module draft, run `scripts/to_module.py` on its files. It adds `module`, turns
  each `import` into `public import`, and opens `@[expose] public section` after the imports.
  Then fix what breaks: private declarations in statements, and module docstrings placed before
  `module`.

## 4. Checking files and building

- `lake build` builds the default targets. `lake build PaperName.Section.File` builds one
  module and what it imports.
- To check a single file against the compiled `.olean`s of its imports, run
  `lake env lean -DautoImplicit=false -DmaxSynthPendingDepth=3 PaperName/Section/File.lean`.
  `lake env lean` does not apply the lakefile's `leanOptions`, so pass the same options with
  `-D`. `scripts/check_file.py` does this, reading the options from `lakefile.toml`.
- Run one build at a time per checkout. Two concurrent `lake build`s, or a build next to an
  editor's `lake setup-file`, can delete each other's outputs ("object file … does not exist").
  Rerun the build when that happens.
- Long builds belong in the background. A clean build of a large development can take tens of
  minutes, even with Mathlib's cache.
- Before spawning repair agents, build once, so that every module's `.olean` exists, with
  `sorry`s, and agents can check their files independently.
- When parallel agents' rebuilds interfere, each agent can check its files against a private
  copy of the build outputs with `scripts/snapshot_check.py` (`take SNAPDIR` while the build is
  fresh, then `check SNAPDIR FILE [--emit]`; see `parallel-repair.md`). Nothing in `.lake`
  changes.

## 5. Common errors when repairing a draft

Drafts written without a compiler fail in predictable ways. Fix the cause, never the symptom. In
particular, do not change a statement to make an error go away.

- **Unknown or renamed constants.** Grep `.lake/packages/mathlib/Mathlib` for the concept. A
  deprecation warning names the replacement.
- **Notation that does not exist.** Drafts invent notation, such as big unions over a `Finset`
  (use `Finset.biUnion`). Check that the notation really parses.
- **Dependent versus non-dependent functions.** `Finset.univ.pi` produces dependent functions;
  `Fintype.piFinset` is usually what is meant.
- **Instance problems.**
  - Missing instances such as `NeZero n`, `Fintype α` or `DecidableEq α`: add the typeclass
    hypothesis, or a `letI`/`haveI` that derives it from an existing hypothesis.
  - Filters over `Prop`-valued predicates need `DecidablePred`. Use `classical` in proofs, and
    give definitions a single classical instance (`Classical.decPred`) so that every lemma sees
    the same one.
  - When two instances clash, state helper lemmas so they do not depend on which instance is
    used, or close the goal with `convert` or `congr`.
- **Implicit arguments that cannot be inferred.** Pass them by name (`(m := m)`), or make them
  explicit.
- **Indices with side conditions.** Definitions such as "the block containing x" may need a
  hypothesis like `0 < m`. An auto-param binder `(h : 0 < m := by assumption)` keeps call sites
  clean. Arithmetic on `Fin` usually needs `have := i.isLt` before `omega`.
- **Section variables.** Typeclass `variable`s are included automatically when the statement
  mentions their type. An included variable that the theorem does not need triggers a linter
  warning; fix it with `omit [Inst] in theorem …`, or by moving the `variable` later.
- **Reserved words.** Identifiers such as `given`, `at` or `from` clash with keywords. Rename them.
- **Order of declarations.** A draft may use a definition before declaring it. Reorder, or move
  the definition to the module that needs it first.
- **Heavy proofs.** Before raising `maxHeartbeats`, split the proof or give `simp` or `ring` a
  smaller goal. If a raise is unavoidable, make it local to that one declaration.
