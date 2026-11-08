# Lean project setup and build discipline

## Contents

1. Versions
2. `lakefile.toml`
3. The module system
4. Checking files and building
5. Common errors when repairing a draft
6. Layout of the project

## 1. Versions

Unless the user pins a version, use the newest Lean release or release candidate that Palomar
accepts (at least the minimum in PalomarSubmission's `toolchains.json`), and pin Mathlib to its
release tag for that toolchain, not to `master`. Palomar renders the Challenge with the release of
the documentation tool Verso for the same toolchain, and the packages that Verso and Mathlib share
must then be pinned at the same revisions. Mathlib's release tag meets this; later `master` commits
soon do not (`palomar.md`, Section 1). The project's `lean-toolchain` must equal the pinned Mathlib
commit's exactly, including any release-candidate suffix.

```sh
lake +leanprover/lean4:<version> new PaperName math   # then set Mathlib's rev to the release tag
lake update                                           # writes lake-manifest.json with the exact Mathlib commit
cat .lake/packages/mathlib/lean-toolchain             # must equal ./lean-toolchain
lake exe cache get                                    # download Mathlib's compiled files
```

Commit `lean-toolchain`, `lakefile.toml` and `lake-manifest.json`. Put `/.lake` in `.gitignore`,
plus `/notes` if the working notes live in the repository directory, and `__pycache__/` if it holds
Python scripts. Never commit `.olean`, `.ilean` or other build outputs.

## 2. `lakefile.toml`

```toml
name = "PaperName"
version = "0.1.0"
keywords = ["math"]
defaultTargets = ["Basic", "External", "PaperName", "Challenge", "Solution"]

[leanOptions]
pp.unicode.fun = true
autoImplicit = false          # catches typos that would otherwise become implicit variables
maxSynthPendingDepth = 3      # Mathlib's own setting

[[require]]
name = "mathlib"
scope = "leanprover-community"
rev = "<release tag>"         # Mathlib's release tag for the version in lean-toolchain

[[lean_lib]]
name = "Basic"
globs = ["Basic.+"]           # general mathematics, which imports only Mathlib (SKILL.md, Phase 2)

[[lean_lib]]
name = "External"
globs = ["External.+"]        # the results the paper cites, which import only Mathlib and Basic

[[lean_lib]]
name = "PaperName"
globs = ["PaperName.+"]       # builds every module under PaperName/; drop it if PaperName.lean imports them all

[[lean_lib]]
name = "Challenge"

[[lean_lib]]
name = "Solution"
```

A library beyond Mathlib that proves a cited result is required the same way, pinned to a full
commit hash (`git = "…"`, `rev = "<commit>"`). A package of the project's own, split out for a
famous result (`references/separate-packages.md`), is required by `path = "../package"` while it is
developed and by its published commit before the project is pushed.

Create `Challenge.lean` and `Solution.lean` with the project, as modules that are empty except for
their imports, so that `lake build` works from the start. Phase 3 fills in the Challenge, and
Phase 6 the Solution. `Solution.lean` can import the whole project and serve as the library's
entry point. Then no separate umbrella file `PaperName.lean` is needed, and the `globs` line keeps
every module in the build.

## 3. The module system

Palomar requires every `.lean` file, scripts included, to begin with `module` (only comments may
come before it; `palomar.md`, Section 1, has the other limits). A module file looks like this:

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

- To convert a draft whose files are not modules, run `scripts/to_module.py` on its files. It adds
  `module`, turns each `import` into `public import`, and opens `@[expose] public section` after
  the imports. Then fix what breaks: private declarations in statements, and module docstrings
  placed before `module`.

## 4. Checking files and building

- `lake build` builds the default targets. `lake build PaperName.Section.File` builds one
  module and what it imports.
- To check a single file against the compiled `.olean`s of its imports, run
  `lake env lean -DautoImplicit=false -DmaxSynthPendingDepth=3 PaperName/Section/File.lean`.
  `lake env lean` does not apply the lakefile's `leanOptions`, so pass the same options with
  `-D`. `scripts/check_file.py` does this, reading the options from `lakefile.toml`.
- Run long builds in the background. A clean build of a large project can take tens of minutes,
  even with Mathlib's cache.
- Before you start repair agents, build once. Then every module's `.olean` exists, with `sorry`s,
  and agents can check their files independently.
- When the rebuilds of parallel agents interfere, each agent can check its files against a private
  copy of the build outputs with `scripts/snapshot_check.py` (`take SNAPDIR` while the build is
  fresh, then `check SNAPDIR FILE [--emit]`; see `parallel-repair.md`). Nothing in `.lake`
  changes.

## 5. Common errors when repairing a draft

Drafts written without a compiler fail in predictable ways. Fix the cause, never the symptom. In
particular, do not change a statement to make an error go away.

- Unknown or renamed constants. Grep `.lake/packages/mathlib/Mathlib` for the concept. A
  deprecation warning names the replacement.
- Notation that does not exist. Drafts invent notation, such as big unions over a `Finset`
  (use `Finset.biUnion`). Check that the notation really parses.
- Dependent versus non-dependent functions. `Finset.univ.pi` produces dependent functions;
  `Fintype.piFinset` is usually what is meant.
- Instance problems:
  - Missing instances such as `NeZero n`, `Fintype α` or `DecidableEq α`: add the typeclass
    hypothesis, or a `letI`/`haveI` that derives it from an existing hypothesis.
  - Filters over `Prop`-valued predicates need `DecidablePred`. Use `classical` in proofs, and
    give definitions a single classical instance (`Classical.decPred`) so that every lemma sees
    the same one.
  - When two instances clash, state helper lemmas so they do not depend on which instance is
    used, or close the goal with `convert` or `congr`.
- Implicit arguments that cannot be inferred. Pass them by name (`(m := m)`), or make them
  explicit.
- Indices with side conditions. Definitions such as "the block containing x" may need a
  hypothesis like `0 < m`. An auto-param binder `(h : 0 < m := by assumption)` keeps call sites
  clean. Arithmetic on `Fin` usually needs `have := i.isLt` before `omega`.
- Section variables. A `variable` enters a theorem only when the statement mentions it or an
  `include` names it.
  - Typeclass `variable`s are included automatically when the statement mentions their type. An
    included variable that the theorem does not need triggers a linter warning. Fix it with
    `omit [Inst] in theorem …`, or by moving the `variable` later.
  - A hypothesis declared as `variable (h : P x)` and mentioned by no statement is the dangerous
    case, and drafts produce it often. Lean leaves `h` out of every statement without a warning,
    so each statement claims more than the draft meant, often something false. The draft's proofs
    that use `h` fail, and its callers that pass `h` get an argument too many; a lemma whose
    proof never used `h` compiles with the stronger statement. Check with `#check` that each
    statement has the hypotheses its proof uses. Add `include h` after the `variable` (or
    `include h in` before a single theorem): this restores the statement the draft meant, so it
    corrects a slip. Record it, with a counterexample to the statement as compiled.
- Reserved words. Identifiers such as `given`, `at` or `from` clash with keywords, `λ` is
  `fun`, and characters such as `₋` and `₊` cannot appear in identifiers. Rename them.
- Order of declarations. A draft may use a definition before declaring it. Reorder, or move
  the definition to the module that needs it first.
- Heavy proofs. Before raising `maxHeartbeats`, split the proof or give `simp` or `ring` a
  smaller goal. If a raise cannot be avoided, make it local to that one declaration.

## 6. Layout of the project

The project has three libraries, in layers, each importing only Mathlib, the layers below it and
itself: `Basic`, general mathematics; `External`, the results of other works that the paper
cites; and `PaperName`, the paper's own results.

```text
Basic/                         -- general mathematics: a library of its own, filed by field
  Algebra/                     -- one directory per field, named as Mathlib names it
  Analysis/Calculus/Rolle.lean -- one file per topic
External/                      -- the results the paper cites from other works: a library of its own
  Topic/                       -- one directory per cited result or source, with a README.md, from the start
PaperName/                     -- the paper's library
  Introduction.lean            -- §1 definitions and statements
  Preliminaries.lean           -- §2
  SectionName/                 -- one directory per major section
    Definitions.lean           -- the section's notation
    Auxiliary.lean             -- lemmas about the paper's objects that are not its results
    Lemma34.lean               -- one file per result, or per small group of results
  Main.lean                    -- the main theorem
Challenge.lean                 -- the main results, in the vocabulary of Mathlib
Solution.lean                  -- their proofs from the library (may double as the root module)
```

Keep general mathematics apart from the start, in a library of its own. A lemma that says nothing
about the paper's objects (a calculus fact, a real inequality, a lemma about probability measures)
goes to `Basic/`, beside `PaperName/` rather than inside it. File it by field, under the directory
that Mathlib uses for that field (`Basic/Algebra/`, `Basic/AlgebraicGeometry/`, `Basic/Analysis/`,
`Basic/Combinatorics/`, `Basic/Probability/`, …), in a file named for its topic, and give it the
name and namespace that Mathlib would give it, so that it can later be contributed to Mathlib or
another library. File it by its mathematics, not by what motivated it: a lemma about graphs goes to
`Combinatorics/` whatever the paper's subject. Only objects that no field of Mathlib covers get a
new field directory, named as Mathlib would name a new area (`Basic/NewArea/`), and
`Basic/README.md` says where each part could go: a new area of Mathlib, proposed on the Lean Zulip
first, or a library for that domain, as PhysLean is for physics.

`Basic` is a `lean_lib` of its own (Section 2), and its files import only Mathlib and each other,
never `External` or the paper's. A cited result that is general is proved there too; its
`External/Topic/README.md` still gives the source and how the paper uses it, and points to the
proof. The definitions that a Challenge statement uses are the exception: they stay in the paper's
module of shared definitions (`references/palomar.md`, Section 2), even the general ones, because
Comparator needs them in one module, and the lemmas about them stay with them until they are
contributed.

Keep the results the paper takes from other works apart too, in `External/`, beside `Basic/` and
`PaperName/`. They are another paper's mathematics, not this one's: another formalization that
cites the same source can reuse them, and the source's own authors can check them. `External` is a
`lean_lib` of its own, and its files import only Mathlib, `Basic` and each other, never the
paper's. Give each source or cited result its own directory `External/Topic/`, with modules
`External.Topic.…` and declarations in the namespace `External.Topic`, each named after the
source's numbering (`External.Author.lemma2`). State each result in the source's own terms, with the
source's definitions (or Mathlib's, or `Basic`'s), not the paper's: the paper's library proves
that the paper's objects are the source's and applies the result, and when the paper's object is
one of the Challenge's definitions, that bridge is often `Iff.rfl` or a short lemma. Decide where
each file belongs when you create it (SKILL.md, Phase 2).
