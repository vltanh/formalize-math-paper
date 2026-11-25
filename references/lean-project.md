# Lean project setup and build discipline

## Contents

1. Versions
2. Layout of the project
3. `lakefile.toml`
4. The module system
5. Checking files and building
6. Common errors when repairing a draft

## 1. Versions

Unless the user pins a version, use the newest Lean release or release candidate that Palomar
accepts (at least the minimum in PalomarSubmission's `toolchains.json`), and pin Mathlib to its
release tag for that toolchain, not to `master`. Palomar renders the Challenge with the release of
the documentation tool Verso for the same toolchain, and the packages that Verso and Mathlib share
must then be pinned at the same revisions. Mathlib's release tag meets this; later `master` commits
soon do not (`palomar.md`, Section 1). The project's `lean-toolchain` must equal the pinned Mathlib
commit's exactly, including any release-candidate suffix.

```sh
lake +leanprover/lean4:<version> new PaperName math     # then set Mathlib's rev to the release tag
lake update                                             # writes lake-manifest.json with the exact Mathlib commit
cat .lake/packages/mathlib/lean-toolchain               # must equal ./lean-toolchain
lake exe cache get                                      # download Mathlib's compiled files
```

Then replace the template's files (`PaperName.lean`, `PaperName/Basic.lean`) and its library with
the layout of Section 2 and the lakefile of Section 3. Commit `lean-toolchain`, `lakefile.toml`
and `lake-manifest.json`. Put `/.lake` and `/notes` in `.gitignore`: `notes/` holds the private
working notes, among them the follow-up papers (SKILL.md, Phase 8). Add `__pycache__/` if the
repository holds Python scripts. Never commit `.olean`, `.ilean` or other build outputs.

## 2. Layout of the project

A project with one paper has this layout. The code, the Palomar files and the documents each have
one place, named after the paper:

```text
README.md                    -- the front page: the paper's README (SKILL.md, Phase 8)
LICENSE                      -- at the root: Palomar reads only the root licence
lakefile.toml, lean-toolchain, lake-manifest.json
PaperName/                   -- all the Lean code, under one root named after the paper
  Basic/                     -- general mathematics, filed by Mathlib area, in Mathlib's namespaces
    README.md                -- where each part could be contributed
    Analysis/Calculus/Rolle.lean
  External/                  -- the results the paper cites from other works
    Source/                  -- one per source, with a README.md; namespace External.Source
  Defs.lean                  -- the definitions that the Challenge copies (when it needs any)
  Introduction.lean          -- the paper's library, by section, in namespace PaperName: §1
  Preliminaries.lean         -- §2
  SectionName/               -- one directory per major section
    Definitions.lean         -- the section's notation
    Auxiliary.lean           -- lemmas about the paper's objects that are not its results
    Lemma34.lean             -- one file per result, or per small group of results
  Main.lean                  -- the main theorem
palomar/PaperName/           -- the paper's Palomar submission
  Challenge.lean             -- module PaperName.Challenge: the main results, in Mathlib's
                                vocabulary, in namespace PaperNameChallenge
  Solution.lean              -- module PaperName.Solution: their proofs from the library
  comparator.json, formalization.yaml
docs/PaperName/              -- the paper's documents
  REPORT.md, CREDITS.md
  paper_routes.tsv, route_differences.tsv
  numerics/                  -- the scripts behind numerical claims, if any (numerics.md)
scripts/                     -- Audit.lean and the tools
.github/workflows/           -- lean_action_ci.yml; palomar_preflight_papername.yml
```

The paper's library is every module of `PaperName/` outside `Basic/` and `External/`: `Defs.lean`,
the sections and `Main.lean`.

A project with several papers keeps a `palomar/PaperName/` and a `docs/PaperName/` for each paper,
and puts the code under one root named after the project: `ProjectName/Common/Basic/` and
`ProjectName/Common/External/`, which the papers share, and one library per paper,
`ProjectName/PaperName/`, laid out as the paper's library above (`multi-paper.md`, Section 2). The
references write `Basic/`, `External/` and "the paper's library" for these directories in either
layout.

A project with one paper keeps the shortest paths. Its modules are `PaperName.Main`,
`PaperName.Basic.…` and `PaperName.External.Source.…`: no directory or module name is repeated, and
the project needs no name besides the paper's. A second paper costs one move: the first paper's code
goes under a root for the project, its `Basic/` and `External/` into `ProjectName/Common/`, and its
modules are renamed (`multi-paper.md`, Section 9). The Palomar files and the documents are already
where several papers put them, and do not move. The Challenge and the Solution keep their module
names, so `comparator.json` and the preflight workflow do not change. The move is made once, with
`git mv` and the tools; until then, every path stays short. The layout also gives the code, the
Palomar files and the documents one predictable place each, for readers and for the tools.

Name the root, the paper's directories and its namespace after the paper (its first author, or a
short title), not after its subject: another paper on the subject may join later, and it needs a
name of its own. Namespaces do not follow directories. The paper's library is in the namespace
`PaperName`; `External/Source/` is in the namespace `External.Source`, and `Basic/` in Mathlib's
namespaces. The Challenge and the Solution are the modules `PaperName.Challenge` and
`PaperName.Solution` of the source directory `palomar/` (Section 3), so `PaperName/` has no file
`Challenge.lean` or `Solution.lean`. The Challenge's theorems are in the namespace
`PaperNameChallenge`: the Solution, which imports the library, restates them under their exact
names, so they need a namespace distinct from the library's and from any other paper's Challenge.

The code has three layers. `Basic/` imports only Mathlib (and the other libraries the project
requires) and itself. `External/` imports the same, `Basic/` and itself. The paper's library imports
anything below it. Nothing in `Basic/` or `External/` imports the paper's library. `Defs.lean` and
the Challenge import only Mathlib, or the libraries that Palomar allows in statements (`palomar.md`,
Section 1), and nothing else of the project. The audit, `scripts/Audit.lean`, imports with
`import all` every module of `PaperName/` and the Solution, never the Challenge, which holds a copy
of the library's definitions under the same names (SKILL.md, Phase 6).

Keep general mathematics apart from the start. A lemma that says nothing about the paper's objects
(a calculus fact, a real inequality, a lemma about probability measures) goes to
`PaperName/Basic/`, not to the paper's library. File it by field, under the directory that Mathlib
uses for that field (`Basic/Algebra/`, `Basic/AlgebraicGeometry/`, `Basic/Analysis/`,
`Basic/Combinatorics/`, `Basic/Probability/`, …), in a file named for its topic, and give it the
name and namespace that Mathlib would give it, so that it can later be contributed to Mathlib or
another library. File it by its mathematics, not by what motivated it: a lemma about graphs goes to
`Combinatorics/` whatever the paper's subject. Only objects that no field of Mathlib covers get a
new field directory, named as Mathlib would name a new area (`Basic/NewArea/`), and
`Basic/README.md` says where each part could go: a new area of Mathlib, proposed on the Lean Zulip
first, or a library for that domain, as PhysLean is for physics.

A cited result that is general is proved in `Basic/` too; its `External/Source/README.md` still
gives the source, how the paper uses it and the argument that proves it, and points to the proof.
The definitions that a Challenge statement uses are the exception: they stay in the paper's
`Defs.lean` (`palomar.md`, Section 2), even the general ones, because Comparator needs them in one
module, and the lemmas about them stay with them until they are contributed.

Keep the results that the paper takes from other works apart too, in `PaperName/External/`. They
are another paper's mathematics, not this one's: another formalization that cites the same source
can reuse them, a later paper of the project that cites the same source shares them, and the
source's own authors can check them. Give each source or cited result its own directory
`External/Source/`, with modules `PaperName.External.Source.…` and declarations in the namespace
`External.Source`, each named after the source's numbering (`External.Author.lemma2`). State each
result in the source's own terms, with the source's definitions (or Mathlib's, or those of
`Basic/`), not the paper's: the paper's library proves that the paper's objects are the source's
and applies the result, and when the paper's object is one of the Challenge's definitions, that
bridge is often `Iff.rfl` or a short lemma. Decide where each file belongs when you create it
(SKILL.md, Phase 2).

## 3. `lakefile.toml`

```toml
name = "PaperName"
version = "0.1.0"
keywords = ["math"]
defaultTargets = ["PaperName", "Palomar"]

[leanOptions]
pp.unicode.fun = true
autoImplicit = false          # catches typos that would otherwise become implicit variables
maxSynthPendingDepth = 3      # Mathlib's own setting

[[require]]
name = "mathlib"
scope = "leanprover-community"
rev = "<release tag>"         # Mathlib's release tag for the version in lean-toolchain

[[lean_lib]]
name = "PaperName"
globs = ["PaperName.+"]       # every module of PaperName/

# Last: Lake gives a module to the last library whose patterns match it, and PaperName.+ also
# matches the Challenge and the Solution.
[[lean_lib]]
name = "Palomar"
srcDir = "palomar"
roots = ["PaperName.Challenge", "PaperName.Solution"]
```

The two libraries are the default targets. The `Palomar` library holds the Challenge and the
Solution, the modules `PaperName.Challenge` and `PaperName.Solution` of the source directory
`palomar/`, and `comparator.json` names them so. Palomar takes a Challenge's source root from its
path, so the source directory `palomar/` is accepted.

Declare the `Palomar` library last. Lake gives a module to the last library whose patterns match
its name, and the glob `PaperName.+` of the code library matches `PaperName.Challenge` and
`PaperName.Solution` too. Declared after the code library, `Palomar` gets them, and everything
builds: `lake build`, `lake build PaperName`, `lake build Palomar` alone, and
`lake build PaperName.Solution` alone, as Comparator runs it. Declared before it, `Palomar` loses
them, and `lake build PaperName.Solution` looks for `PaperName/Solution.lean` and fails. (Tested
with Lean v4.37.0-rc1.) The `Palomar` library lists its modules by name, in `roots`, not by a
glob: a glob `PaperName.+` there would also match the modules of `PaperName/`, which Lake would
then look for in `palomar/`, and whether `lake build Palomar` alone works would depend on the
order of the libraries.

Lake fails on a root whose file does not exist. Create `palomar/PaperName/Challenge.lean` and
`Solution.lean` with the project, as modules that are empty except for their imports, so that
`lake build` works from the start. Phase 3 fills in the Challenge, and Phase 6 the Solution. The
Solution imports the paper's library and serves as its entry point. No umbrella file
`PaperName.lean` is needed: the glob keeps every module of `PaperName/` in the build, and it does
not match `PaperName.lean` itself.

A library beyond Mathlib that proves a cited result is required the same way, pinned to a full
commit hash (`git = "…"`, `rev = "<commit>"`). A package of the project's own, split out for a
theory that Lean lacks (`references/separate-packages.md`), is required by `path = "../package"` while it is
developed and by its published commit before the project is pushed.

With several papers, the lakefile has a library `Common` and one library per paper, and the
`Palomar` library, still last, lists every paper's two modules (`multi-paper.md`, Section 2).

## 4. The module system

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

## 5. Checking files and building

- `lake build` builds the default targets. `lake build PaperName.SectionName.File` builds one
  module and what it imports.
- To check a single file against the compiled `.olean`s of its imports, run
  `lake env lean -DautoImplicit=false -DmaxSynthPendingDepth=3 PaperName/SectionName/File.lean`.
  `lake env lean` does not apply the lakefile's `leanOptions`, so pass the same options with
  `-D`. `scripts/check_file.py` does this, reading the options from `lakefile.toml`; for a file
  under `palomar/` it also passes `-R palomar`, so that the file's module is `PaperName.Challenge`
  as in the build.
- Run long builds in the background. A clean build of a large project can take tens of minutes,
  even with Mathlib's cache.
- Before you start repair agents, build once. Then every module's `.olean` exists, with `sorry`s,
  and agents can check their files independently.
- When the rebuilds of parallel agents interfere, each agent can check its files against a private
  copy of the build outputs with `scripts/snapshot_check.py` (`take SNAPDIR` while the build is
  fresh, then `check SNAPDIR FILE [--emit]`; see `parallel-repair.md`). Nothing in `.lake`
  changes.

## 6. Common errors when repairing a draft

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
