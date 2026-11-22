# Several papers in one repository

Some formalizations are about a question, not a paper: a theorem and the paper that sharpens it,
two papers that settle complementary cases of one problem, a claimed proof and the work that
answers it. Formalizing them in one repository lets the papers share code (general lemmas, cited
results, bridges between their definitions) and lets one paper's library use another's results
instead of assuming them. Each paper still keeps everything a reader or a registry looks at for
that paper on its own: its statements of record, its audit, its credits, its Palomar submission.
A central README ties them together.

Every project already has the layout that several papers need (`lean-project.md`, Section 2). This
guide says only what changes when there are several.

## Contents

1. When to combine papers
2. Layout
3. Definitions and Challenges
4. Results that cross papers
5. Routes, audit and findings
6. Documents
7. Palomar
8. Tools
9. Moving an older repository to the standard layout

## 1. When to combine papers

Combine papers when they share mathematics that would otherwise be written twice, or when one
paper's proof uses another's results: a sequel, a paper and its correction, papers on complementary
cases of one problem, a survey of claims on one question. Keep unrelated papers in separate
repositories, even by the same author: a shared repository only adds coupling.

The user decides. When a second paper arrives for an existing project, ask whether it joins the
repository or starts a new one (Phase 0), unless the request already says so.

## 2. Layout

The standard layout (`lean-project.md`, Section 2) already has a place for every paper. Each paper
adds its library `ProjectName/PaperName/`, its Palomar submission `palomar/PaperName/` and its
documents `docs/PaperName/`; nothing else moves. `ProjectName/Common/`, `scripts/`, the licence and
the lakefile stay shared, and a result that two papers cite is formalized once, in
`Common/External/`. Two documents change: the root README becomes the umbrella document
(Section 6), and each paper's README goes to `docs/PaperName/README.md`.

For each paper, the lakefile (`lean-project.md`, Section 3) gains a `lean_lib` for its library
(`name = "PaperB"`, `globs = ["ProjectName.PaperB.+"]`) among the default targets, and the paper's
name in the `globs` of the `Palomar` library once `palomar/PaperB/` exists. Name each paper after
the paper, not after the subject (`lean-project.md`, Section 2): two papers on one subject need
different names.

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
  generates these lines (in `assets/Audit.lean`) and CI's check of them already cover every paper;
  add each paper's name to the check's `grep` pattern, and each paper's Solution module to
  `isLibraryModule`. The audit lists every paper's numbered results (with the paper in the label:
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
already registered stays pinned to the commit it was submitted at: moving it to the standard layout
(Section 9) does not change that entry, and whether to resubmit it from the new layout is the
user's decision.

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
- CI (`assets/lean_action_ci.yml`): every paper's name in the `grep` pattern of the audit-import
  check; the route check once per paper; the sync check, the links and the tables for every paper.

## 9. Moving an older repository to the standard layout

An older repository may keep `Basic/`, `External/` and `PaperName/` at the root, with
`Challenge.lean`, `Solution.lean`, `comparator.json`, `formalization.yaml`, `REPORT.md`,
`CREDITS.md` and `NEXT.md` beside them, and the routes in `docs/`. Move it to the standard layout
before a second paper's statements are written, or whenever the user asks:

1. Move the files with `git mv`, so that history follows them:
   - `PaperName/` to `ProjectName/PaperName/`; its modules become `ProjectName.PaperName.…`. If its
     namespace was named after the subject, rename it after the paper, and its Challenge namespace
     to `PaperNameChallenge`;
   - `Basic/` and `External/` to `ProjectName/Common/`; their modules become
     `ProjectName.Common.Basic.…` and `ProjectName.Common.External.…`, and their namespaces stay;
   - `Challenge.lean`, `Solution.lean`, `comparator.json` and `formalization.yaml` to
     `palomar/PaperName/`; the modules become `PaperName.Challenge` and `PaperName.Solution`;
   - `REPORT.md`, `CREDITS.md`, the two routes files and any numerics scripts (into `numerics/`) to
     `docs/PaperName/`, and `NEXT.md` there with a plain `mv`, since git does not track it. The
     README stays at the root while the repository holds one paper.
2. Rewrite the imports of every `.lean` file, scripts included, and the module names in
   `comparator.json`. Point the tools at the new paths: the lakefile (`lean-project.md`,
   Section 3), the audit's `import all` lines and `isLibraryModule`, CI, `sync_challenge_defs.py`,
   the configuration of `linkify_docs.py`, and the preflight workflow, renamed
   `palomar_preflight_papername.yml`, whose `options` name both paths. Ignore `NEXT.md` in every
   directory (`NEXT.md` in `.gitignore`, without a leading slash). Delete the old build outputs
   under `.lake/build`: stale `.ilean` files make `linkify_docs.py` link to the old paths.
3. Rewrite every relative link of the moved documents, and of the README, which now points into
   `docs/PaperName/` and `palomar/PaperName/`: resolve each link against the document's old
   directory, map the target to its new path, and make it relative to the document's new
   directory. Then rerun `linkify_docs.py`.
4. Check the move. Rebuild, rerun every check of Phase 6 (audit, route check, Comparator, Palomar's
   local checks), and run `scripts/stmt_diff.py` against the commit before the move; it follows
   renamed files. The move must change no statement and no proof's route, apart from the renames.
5. Commit the move on its own, with a message that lists the renames, before any new mathematics.
   A branch that already holds work on a new paper takes the move by a merge: git places most moved
   files by its rename detection, but files the branch added in a moved directory need to be moved
   by hand, and their imports rewritten.

When the second paper then joins, move the first paper's README to `docs/PaperName/README.md`
(rewriting its links as in step 3), write the umbrella README (Section 6), and split any
definitions that the second paper also needs into that paper's own `Defs.lean` (Section 3): the
first paper's Challenge must not grow definitions it does not use.
