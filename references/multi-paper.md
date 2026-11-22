# Several papers in one repository

Some formalizations are about a question, not a paper: a theorem and the paper that sharpens it,
two papers that settle complementary cases of one problem, a claimed proof and the work that
answers it. Formalizing them in one repository lets the papers share code (general lemmas, cited
results, bridges between their definitions) and lets one paper's library use another's results
instead of assuming them. Each paper still keeps everything a reader or a registry looks at for
that paper on its own: its statements of record, its audit, its credits, its Palomar submission.
A central README ties them together.

A project with one paper has all its code under `PaperName/` (`lean-project.md`, Section 2). With
several papers, the code is under one root named after the project, with the code that the papers
share in `Common/`; `palomar/` and `docs/` have one directory per paper, as they do for one paper.
This guide gives that layout, what else changes when there are several papers, and how a project
of one paper takes a second (Section 9).

## Contents

1. When to combine papers
2. Layout
3. Definitions and Challenges
4. Results that cross papers
5. Routes, audit and findings
6. Documents
7. Palomar
8. Tools
9. From one paper to several

## 1. When to combine papers

Combine papers when they share mathematics that would otherwise be written twice, or when one
paper's proof uses another's results: a sequel, a paper and its correction, papers on complementary
cases of one problem, a survey of claims on one question. Keep unrelated papers in separate
repositories, even by the same author: a shared repository only adds coupling.

The user decides. When a second paper arrives for an existing project, ask whether it joins the
repository or starts a new one (Phase 0), unless the request already says so. A paper that joins a
project of one paper starts with the move of Section 9.

## 2. Layout

```text
README.md                    -- the umbrella README (Section 6)
LICENSE, lakefile.toml, lean-toolchain, lake-manifest.json
ProjectName/                 -- all the Lean code, under one root named after the project
  Common/Basic/              -- general mathematics, shared, in Mathlib's namespaces
  Common/External/Source/    -- cited results, shared, with a README.md; namespace External.Source
  PaperA/                    -- paper A's library, in namespace PaperA
    Defs.lean, Introduction.lean, …, Main.lean
  PaperB/
palomar/PaperA/              -- paper A's submission: Challenge.lean (module PaperA.Challenge),
                                Solution.lean (PaperA.Solution), comparator.json, formalization.yaml
palomar/PaperB/
docs/PaperA/                 -- paper A's documents: README.md, REPORT.md, CREDITS.md, the routes,
                                NEXT.md (private), numerics/
docs/PaperB/
scripts/                     -- one Audit.lean for the repository, and the tools
.github/workflows/           -- lean_action_ci.yml; palomar_preflight_papera.yml, …_paperb.yml
```

Each paper has its library `ProjectName/PaperName/`, laid out as the library of one paper
(`Defs.lean`, the sections, `Main.lean`; `lean-project.md`, Section 2), its Palomar submission
`palomar/PaperName/` and its documents `docs/PaperName/`. `ProjectName/Common/`, `scripts/`, the
licence and the lakefile are shared, and a result that two papers cite is formalized once, in
`Common/External/`. Two documents change: the root README becomes the umbrella document
(Section 6), and each paper's README goes to `docs/PaperName/README.md`.

Name the root after the project: its question or subject (`Morrey/`), or one of its papers, as
when a second paper joins a project of one paper and the first paper's name stays the root
(`Smith/Common/`, `Smith/Smith/`, `Smith/Jones/`; Section 9). Name each paper after the paper, not
after the subject (`lean-project.md`, Section 2): two papers on one subject need different names.
The modules of `ProjectName/PaperA/` are `ProjectName.PaperA.…`, and their declarations are in the
namespace `PaperA`; `Common/Basic/` is in Mathlib's namespaces, and `Common/External/Source/` in
`External.Source`. Each paper's Challenge and Solution are the modules `PaperA.Challenge` and
`PaperA.Solution` of the source directory `palomar/`, and the Challenge's theorems are in the
namespace `PaperAChallenge`, as for one paper. The layers are those of one paper, with
`Common/Basic/` and `Common/External/` shared (Section 4).

The lakefile (`lean-project.md`, Section 3) has a library for `Common/` and one per paper, and the
`Palomar` library lists every paper's two modules:

```toml
name = "ProjectName"
defaultTargets = ["Common", "PaperA", "PaperB", "Palomar"]

[[lean_lib]]
name = "Common"
globs = ["ProjectName.Common.+"]     # Common/Basic/ and Common/External/

[[lean_lib]]
name = "PaperA"
globs = ["ProjectName.PaperA.+"]     # every module of paper A's library

[[lean_lib]]
name = "PaperB"
globs = ["ProjectName.PaperB.+"]

# Last, as for one paper (lean-project.md, Section 3).
[[lean_lib]]
name = "Palomar"
srcDir = "palomar"
roots = ["PaperA.Challenge", "PaperA.Solution", "PaperB.Challenge", "PaperB.Solution"]
```

Every library is a default target. The `Palomar` library lists its modules by name: when a paper
is named as the project, its Challenge (`Smith.Challenge`, in `palomar/`) and the shared code
(`Smith.Common.Basic.…`, at the root) are modules of one root, and a glob `Smith.+` in `Palomar`
would match both (`lean-project.md`, Section 3). Declare it last, as for one paper: Lake gives a
module to the last library whose patterns match it, so no other library can then take a Challenge
or a Solution. Lake fails on a glob whose directory, or a root whose file, does not exist: add a
paper's library, or its two modules to the `roots`, only once they exist (a `README.md` in
`Common/Basic/` is enough to create that directory).

## 3. Definitions and Challenges

Each paper has its own Challenge, and each Challenge is checked on its own: by a reader, by
Comparator and by Palomar's review. So each paper's `Defs.lean` holds every definition its
Challenge uses, imports exactly what its Challenge imports (Mathlib, or the libraries Palomar
allows), and is a single module, for the reason `palomar.md`, Section 2, gives (Comparator compares
the auxiliary lemmas that elaboration creates, so the Challenge's copy must come from one module
elaborated the same way). Two papers' Challenges therefore never share a definitions module.

Each Challenge's theorems live in its paper's namespace (`PaperAChallenge`), never a generic one
such as `Challenge`: the audit imports every paper's Solution, and each Solution restates its
Challenge's theorems under their exact names, so two papers with one Challenge namespace clash.

State each paper's definitions in that paper's own terms, even when two papers define the same
notion. Papers often differ in the details (one tests quasiconvexity with smooth compactly
supported maps, another with Lipschitz maps vanishing on the boundary; one asks convexity along
lines, another on segments), and each paper's statements are faithful only in its own terms. Prove
the bridges between the two forms in the library (Section 4): they are the evidence that the papers
talk about the same thing.

## 4. Results that cross papers

- A paper whose proof uses another paper of the repository imports that paper's library instead of
  stating the result in `Common/External/` as an axiom: the result is formalized, so it is proved.
  Record the dependency in the later paper's report and routes as a use of a cited result
  (Section 2 of its report), naming the sibling paper's theorem.
- Bridges between two papers' definitions, and results that combine several papers, go in the
  library of the paper that claims them (a paper that says "together with [earlier paper], this
  settles every case but one" owns that combined theorem), or, when no paper claims them, in the
  library of the later paper. Never under `Common/`, which imports no paper's library.
- `Common/Basic/` and `Common/External/` keep their layering (`lean-project.md`, Section 2):
  `Common/Basic/` imports only Mathlib, `Common/External/` only Mathlib and `Common/Basic/`, and no
  paper's library is imported by them.

## 5. Routes, audit and findings

- Each paper has its own `docs/PaperName/paper_routes.tsv` and
  `docs/PaperName/route_differences.tsv`. Labels must be unique across the repository: the audit
  maps every declaration to the label in its docstring, and a later paper's routes cite an earlier
  paper's results by label. TeX labels often collide (`thm:main`), so compare the papers' labels
  before writing a new paper's statements (`cut -f1` of the routes files), and when they collide,
  prefix the new paper's labels (`jones:thm:main`) in its routes files and in its docstrings. For a
  paper without TeX source (an old journal article) invent prefixed labels (`sv-lemma1`) and record
  them in that paper's routes file with a comment. A sibling paper's result that a proof cites is a
  row of the citing paper's routes file, added by hand (the TeX cites the sibling with `\cite`,
  which the extractor does not see), with `proved = 0` and the sibling's label.
- One `scripts/Audit.lean` covers the whole repository. It imports, with `import all`, every module
  of `ProjectName/` and every paper's Solution, but no Challenge: a Challenge holds a copy of its
  paper's definitions under the library's names, and the two copies clash. The command that
  generates these lines (in `assets/Audit.lean`) and CI's check of them cover every paper once
  they `find ProjectName` instead of `PaperName`; add each paper's name to the check's `grep`
  pattern, and let `isLibraryModule` accept the root `ProjectName` and each paper's Solution
  module. The audit lists every paper's numbered results (with the paper in the label:
  "Šverák Lemma 1") and every paper's Comparator theorems, and checks every declaration's axioms.
  It writes one `.lake/route_deps.tsv`; run the route check once per paper, with that paper's two
  files:
  `python3 scripts/route_check.py check docs/PaperA/paper_routes.tsv --accept docs/PaperA/route_differences.tsv`.
- Findings are numbered within each paper's report (E1, E2, … in each), so that a paper's report
  can be read, cited and submitted on its own. A finding that concerns two papers (one paper's
  claim refuted by another's theorem) appears in both reports, each with its own number and a link
  to the other.

## 6. Documents

Each paper keeps its documents in `docs/PaperName/`, as in every project, and its README joins them
there: `README.md`, `REPORT.md`, `CREDITS.md` and the private `NEXT.md`, written as
`audit-report.md`, `credits.md` and `next-papers.md` say, for that paper alone. A paper's README
links to the umbrella README and to the sibling papers it uses.

The umbrella `README.md` at the root is the repository's front page. It describes the question,
not one paper:

1. Title, CI badge, and a short account of the problem for a mathematician.
2. The state of the problem: a table of its cases (the cells of the problem's landscape) with what
   is known in each, which paper settles it, and whether that is formalized here (proved,
   conditional, refuted, open).
3. The papers: one row per paper, with its claim, the status of its formalization, its main
   finding, and links to its README, REPORT and Challenge.
4. The literature review connecting the papers: the history of the problem, how each paper builds
   on, answers or complements the others, their versions and corrections, the later work, and other
   formalizations. It draws on the papers' own literature sections (each report's Section 10) and
   is checked the same way, independently of its writer. The per-paper sections stay focused on
   their paper; the umbrella is where the connections are made.
5. What the repository adds beyond the papers: theorems that combine them, bridges between their
   definitions, and refutations.
6. Trust (the build, the audit, Comparator, reviews), the shared code (`Common/`), building, and the
   layout.
7. Credits: one line per paper and round, linking to each paper's `CREDITS.md`; the license.

Rewrite the umbrella README whole at the end of each round, like a paper's README. When the user
asks for follow-up papers across the question rather than one paper, a central private `NEXT.md`
at the root may replace or complement the per-paper ones; the `.gitignore` line `NEXT.md`, without
a leading slash, keeps every one of them out of git.

## 7. Palomar

Each paper is its own Palomar submission, with its files in `palomar/PaperName/` and a preflight
workflow whose `options` name both of them, as in every project (`palomar.md`, Sections 1 and 8).
Palomar accepts several submissions in one repository: each names its own Comparator configuration
and metadata, and only the licence must be the single root file. What several papers add:

- each paper's `formalization.yaml` names, in `related_formalizations`, the sibling papers' entries
  in the same repository (with `relationship: other` and a note), and cites in `sources` the
  sibling papers it uses, as `background`;
- one preflight workflow per paper (`.github/workflows/palomar_preflight_papera.yml`,
  `palomar_preflight_paperb.yml`, …), each with its own paper's two paths;
- Palomar's local checks run once per paper, with the metadata path of that paper; the source
  checks cover the whole repository.

Each submission is reviewed and registered on its own, so each needs the user's permission on its
own (SKILL.md, Rules).

Palomar reviews a commit of the whole repository. Its source checks read every `.lean` file (the
module header, at most 10,000 lines, no symbolic links), so a paper still in progress must meet
them too; its `sorry`s do not fail them. But they fail the shared audit, and so the CI of the
finished papers: keep the default branch building and audited, and develop a new paper on a branch
until its proofs are done (its statements, once checked, are that branch's baseline). A paper
already registered stays pinned to the commit it was submitted at: moving its code (Section 9)
does not change that entry, and whether to resubmit it from the new layout is the user's
decision.

## 8. Tools

- `sync_challenge_defs.py`: one `(definitions module, Challenge)` pair per paper in `PAIRS`
  (`('ProjectName/PaperA/Defs.lean', 'palomar/PaperA/Challenge.lean')`); `--check` checks every
  pair.
- `linkify_docs.py`: every paper's documents, its README included, and the umbrella README in
  `DOCS`; in `NAMESPACES_BY_DIR`, each paper's document directory with its namespaces, the
  library's first and then the Challenge's (`{'docs/PaperA': ['PaperA', 'PaperAChallenge'], …}`),
  so that a short name in a paper's documents links to that paper's declaration; `MODULE_ROOTS`:
  `ProjectName` and every paper's name (the root of its Challenge and Solution modules);
  `SOURCE_DIRS`: `{'PaperA': 'palomar', …}`; `PREFERRED_MODULE`: a tuple of every paper's
  Challenge, so that a definition links to the Challenge's copy; `PATH_BASES`: each paper's
  document directory with its own Palomar directory (`{'docs/PaperA': ['palomar/PaperA'], …}`), so
  that `Challenge.lean` in a paper's documents names that paper's file, and none for the umbrella
  README. Links are relative to each document's directory. A short name of fewer than four
  characters is never looked up (it reads as a variable): write it qualified (`PaperA.jac`).
- `check_md_tables.py`: run it on every document.
- CI (`assets/lean_action_ci.yml`): in the check of the audit's imports, `find ProjectName` and
  every paper's name in the `grep` pattern; the route check once per paper; the sync check, the
  links and the tables for every paper.

## 9. From one paper to several

When a second paper joins a project of one paper, the first paper's code moves under a root for
the project (Section 2). Make the move before the second paper's statements are written:

1. Choose the root: a new name for the question, or the first paper's name, which then names the
   project and the paper (`Smith/Smith/`). Move the files with `git mv`, so that history follows
   them:
   - `PaperName/Basic/` to `ProjectName/Common/Basic/`, and `PaperName/External/` to
     `ProjectName/Common/External/`; their modules `PaperName.Basic.…` and `PaperName.External.…`
     become `ProjectName.Common.Basic.…` and `ProjectName.Common.External.…`, and their namespaces
     stay;
   - the rest of `PaperName/` to `ProjectName/PaperName/`; its modules `PaperName.X` become
     `ProjectName.PaperName.X`, and its namespace stays `PaperName`.

   With a new root:

   ```sh
   mkdir -p ProjectName/Common
   git mv PaperName/Basic PaperName/External ProjectName/Common/
   git mv PaperName ProjectName/PaperName
   ```

   With the paper's name as the root:

   ```sh
   mkdir -p PaperName/Common PaperName/PaperName
   git mv PaperName/Basic PaperName/External PaperName/Common/
   for f in PaperName/*; do
     case $f in PaperName/Common|PaperName/PaperName) ;; *) git mv "$f" PaperName/PaperName/ ;; esac
   done
   ```

   `palomar/PaperName/` and `docs/PaperName/` do not move, and the Challenge and the Solution keep
   their module names: `comparator.json`, `formalization.yaml` and the preflight workflow do not
   change.
2. Rename the moved modules in every `.lean` file, scripts included, and in the documents (the
   README, `REPORT.md`, `CREDITS.md`, the READMEs of `Basic/` and `External/`). Rename each module
   by its exact old name, from the list of moved files (`git diff --cached -M --name-status`), not
   by a prefix: the declarations keep their names, and `PaperName.theorem1_1` must not become
   `ProjectName.PaperName.theorem1_1`. Rewrite the paths that the documents name the same way
   (`PaperName/Basic/` becomes `ProjectName/Common/Basic/`).
3. Point the tools at the new paths: the lakefile, with the library `Common`, one library per
   paper, and `Palomar` last (Section 2); the audit's `import all` lines, generated again, and
   `isLibraryModule`; CI's check of the audit's imports (`find ProjectName`, and every paper's name
   in the `grep` pattern); `sync_challenge_defs.py`; and the configuration of `linkify_docs.py`
   (Section 8). Delete the old build outputs under `.lake/build`: stale `.ilean` files make
   `linkify_docs.py` link to the old paths.
4. Check the move. Rebuild, and build `Palomar` and the Solution alone
   (`lake build PaperName.Solution`), as Comparator does. Rerun every check of Phase 6 (audit,
   route check, Comparator, Palomar's local checks), and `linkify_docs.py`, which recomputes every
   link to a line of the code and warns about a code span that names nothing any more. Run
   `scripts/stmt_diff.py` against the commit before the move; it follows renamed files. The move
   must change no statement and no proof's route: `stmt_diff.py` lists only renames.
5. Commit the move on its own, with a message that lists the renames, before any new mathematics.
   A branch that already holds work on the new paper takes the move by a merge: git places most
   moved files by its rename detection, but files the branch added in a moved directory need to be
   moved by hand, and their imports rewritten.

Then the second paper joins. Move the first paper's README to `docs/PaperName/README.md` and
rewrite its relative links: resolve each link against the root, and make it relative to
`docs/PaperName/`. Write the umbrella README (Section 6), list every paper's documents in the
configuration of `linkify_docs.py`, and rerun it. Split any definitions that the second paper also
needs into that paper's own `Defs.lean` (Section 3): the first paper's Challenge must not grow
definitions it does not use.

An older repository may keep `Basic/`, `External/` and `PaperName/` at the root, with
`Challenge.lean`, `Solution.lean`, `comparator.json`, `formalization.yaml`, `REPORT.md`,
`CREDITS.md` and `NEXT.md` beside them, and the routes in `docs/`. Move it to the layout of one
paper (`lean-project.md`, Section 2) whenever the user asks, with these moves in place of step 1,
and then steps 2 to 5 with the lakefile of `lean-project.md`, Section 3. When a second paper is
joining, move it straight to the layout of Section 2 instead (`Basic/` and `External/` to
`ProjectName/Common/`, `PaperName/` to `ProjectName/PaperName/`).

- `Basic/` and `External/` to `PaperName/Basic/` and `PaperName/External/`; their modules become
  `PaperName.Basic.…` and `PaperName.External.…`, their namespaces stay, and the paper's library
  stays where it is. If its namespace was named after the subject, rename it after the paper, and
  its Challenge namespace to `PaperNameChallenge`;
- `Challenge.lean`, `Solution.lean`, `comparator.json` and `formalization.yaml` to
  `palomar/PaperName/`; the modules become `PaperName.Challenge` and `PaperName.Solution`, and
  `comparator.json` names them so. Rename the preflight workflow `palomar_preflight_papername.yml`,
  and let its `options` name both paths;
- `REPORT.md`, `CREDITS.md`, the two routes files and any numerics scripts (into `numerics/`) to
  `docs/PaperName/`, and `NEXT.md` there with a plain `mv`, since git does not track it (`NEXT.md`
  in `.gitignore`, without a leading slash). Rewrite every relative link of the moved documents,
  and of the README, which stays at the root: resolve each link against the document's old
  directory, map the target to its new path, and make it relative to the document's new directory.
