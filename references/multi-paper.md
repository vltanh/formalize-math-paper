# Several papers in one repository

Some formalizations are about a question, not a paper: a theorem and the paper that sharpens it,
two papers that settle complementary cases of one problem, a claimed proof and the work that
answers it. Formalizing them in one repository lets the papers share code (general lemmas, cited
results, bridges between their definitions) and lets one paper's library use another's results
instead of assuming them. Each paper still keeps everything a reader or a registry looks at for
that paper on its own: its statements of record, its audit, its credits, its Palomar submission.
A central README ties them together.

## Contents

1. When to combine papers
2. Layout
3. Definitions and Challenges
4. Results that cross papers
5. Routes, audit and findings
6. Documents
7. Palomar
8. Tools
9. Adding a paper to an existing repository

## 1. When to combine papers

Combine papers when they share mathematics that would otherwise be written twice, or when one
paper's proof uses another's results: a sequel, a paper and its correction, papers on complementary
cases of one problem, a survey of claims on one question. Keep unrelated papers in separate
repositories, even by the same author: a shared repository only adds coupling.

The user decides. When a second paper arrives for an existing project, ask whether it joins the
repository or starts a new one (Phase 0), unless the request already says so.

## 2. Layout

The code, the Palomar files and the documents each have a directory of their own, and inside each
of them every paper has a subdirectory named after it:

```text
README.md                 -- the umbrella document (Section 6)
LICENSE                   -- once, at the root (Palomar reads only the root licence)
lakefile.toml, lean-toolchain, lake-manifest.json
<Project>/                -- the Lean code, under one root named after the question (e.g. Morrey/)
  Common/Basic/           -- general mathematics, shared
  Common/External/        -- cited results, shared: a result two papers cite is formalized once
  PaperA/                 -- PaperA's library, by section as for a single paper
    Defs.lean             -- every definition PaperA's Challenge uses, self-contained (Section 3)
  PaperB/                 -- the same
palomar/                  -- one Palomar submission per paper
  PaperA/
    Challenge.lean        -- module PaperA.Challenge
    Solution.lean         -- module PaperA.Solution, PaperA's entry point
    comparator.json, formalization.yaml
  PaperB/
docs/                     -- the documents of each paper
  PaperA/
    README.md, REPORT.md, CREDITS.md
    paper_routes.tsv, route_differences.tsv
    NEXT.md               -- private, ignored by git (Phase 8)
  PaperB/
scripts/                  -- the shared tools, configured for every paper (Section 8)
.github/workflows/        -- CI for every paper; one preflight workflow per paper
```

Name each paper's subdirectories and its namespace after the paper (first author, or a short
title), not after the subject: the subject is the repository's, and two papers on one subject need
different names. The namespaces do not follow the directories: the library of `<Project>/PaperA/`
is in namespace `PaperA`, `Common/External/<Source>/` in `External.<Source>`, and `Common/Basic/`
in Mathlib's namespaces.

The lakefile has one `lean_lib` per paper's library (`name = "PaperA"`,
`globs = ["<Project>.PaperA.+"]`), one for `Common` (`globs = ["<Project>.Common.+"]`), and one for
the Challenges and Solutions, whose source directory is `palomar/`:

```toml
[[lean_lib]]
name = "Palomar"
srcDir = "palomar"
globs = ["PaperA.+", "PaperB.+"]   -- only papers whose palomar/ directory exists: Lake fails on a missing one
```

so that the Challenge and Solution modules are `PaperA.Challenge` and `PaperA.Solution`, and the
Comparator configuration names them so. Palomar takes a Challenge's source root from its path
(`palomar/` here), so this layout is accepted.

Decide the layout before the second paper's statements are written. Moving a paper's files later
rewrites module names, the audit's list of modules, the routes, every document's links and the
Palomar files, and conflicts with any branch that touches them (Section 9).

## 3. Definitions and Challenges

Each paper has its own Challenge, and each Challenge is checked on its own: by a reader, by
Comparator and by Palomar's review. So each paper's definitions module holds every definition its
Challenge uses, imports exactly what its Challenge imports (Mathlib, or the libraries Palomar
allows), and lives in one module, for the reason `palomar.md`, Section 2, gives (Comparator
compares the auxiliary lemmas that elaboration creates, so the Challenge's copy must come from one
module elaborated the same way). Two papers' Challenges therefore never share a definitions module.

Each Challenge's theorems live in a namespace of the paper's own (`PaperAChallenge`), not a generic
one such as `Challenge`: the audit imports every paper's Solution, and each Solution restates its
Challenge's theorems under their exact names, so two papers with one Challenge namespace clash.

State each paper's definitions in that paper's own terms, even when two papers define the same
notion. Papers often differ in the details (one tests quasiconvexity with smooth compactly
supported maps, another with Lipschitz maps vanishing on the boundary; one asks convexity along
lines, another on segments), and each paper's statements are faithful only in its own terms. Prove
the bridges between the two forms in the library (Section 4): they are the evidence that the papers
talk about the same thing.

## 4. Results that cross papers

- A paper whose proof uses another paper of the repository imports that paper's library instead of
  stating the result in `External/` as an axiom: the result is formalized, so it is proved.
  Record the dependency in the later paper's report and routes as a use of a cited result
  (Section 2 of its report), naming the sibling paper's theorem.
- Bridges between two papers' definitions, and results that combine several papers, go in the
  library of the paper that claims them (a paper that says "together with [earlier paper], this
  settles every case but one" owns that combined theorem), or, when no paper claims them, in a small
  shared module under `Common/` imported by neither paper's Challenge.
- `Common/Basic/` and `Common/External/` keep the layering of a single-paper project: `Basic`
  imports only Mathlib, `External` only Mathlib and `Basic`, and no paper's library is imported by
  them.

## 5. Routes, audit and findings

- Each paper has its own `docs/PaperA/paper_routes.tsv` and `docs/PaperA/route_differences.tsv`.
  Labels must be unique across the repository: the audit maps every declaration to the label in
  its docstring, and a later paper's routes cite an earlier paper's results by label. TeX labels
  often collide (`thm:main`), so compare the papers' labels before writing a new paper's statements
  (`cut -f1` of the routes files), and when they collide, prefix the new paper's labels
  (`jones:thm:main`) in its routes files and in its docstrings. For a paper without TeX source (an
  old journal article) invent prefixed labels (`sv-lemma1`) and record them in that paper's routes
  file with a comment. A sibling paper's result that a proof cites is a row of the
  citing paper's routes file, added by hand (the TeX cites the sibling with `\cite`, which the
  extractor does not see), with `proved = 0` and the sibling's label.
- One `scripts/Audit.lean` covers the whole repository. It imports every library module and every
  paper's Solution with `import all`, but no Challenge: a Challenge holds a copy of its paper's
  definitions under the library's names, and the two copies clash. Generate the lines with
  `{ find <Project> -name '*.lean'; cd palomar && find . -name Solution.lean; } | sed …`, and give
  the CI step that checks the audit's imports the same command; `isLibraryModule` accepts the
  `<Project>` root and the papers' Solution modules. The audit lists every paper's
  numbered results (with the paper in the label: "Šverák Lemma 1") and every paper's Comparator
  theorems, sets `isLibraryModule` to every library root, and checks every declaration's axioms. It
  writes one `.lake/route_deps.tsv`; run the route check once per paper, with that paper's two
  files:
  `python3 scripts/route_check.py check docs/PaperA/paper_routes.tsv --accept docs/PaperA/route_differences.tsv`.
- Findings are numbered within each paper's report (E1, E2, … in each), so that a paper's report
  can be read, cited and submitted on its own. A finding that concerns two papers (one paper's
  claim refuted by another's theorem) appears in both reports, each with its own number and a link
  to the other.

## 6. Documents

Each paper keeps the documents of a single-paper project, in `docs/PaperA/`: `README.md`,
`REPORT.md`, `CREDITS.md` and the private `NEXT.md`, written as `audit-report.md`, `credits.md` and
`next-papers.md` say, for that paper alone. A paper's README links to the umbrella README and to
the sibling papers it uses.

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
at the root may replace or complement the per-paper ones.

## 7. Palomar

Each paper is its own Palomar submission. Palomar accepts several in one repository: a submission
names its Comparator configuration (`comparator_config_path`) and its metadata
(`formalization_metadata_path`), both repository-relative, and the Challenge and Solution modules
come from the configuration (`challenge_module: "PaperA.Challenge"`). Only the licence must be the
single root file. So:

- `palomar/PaperA/comparator.json` names `PaperA.Challenge` and `PaperA.Solution` and PaperA's
  theorems;
- `palomar/PaperA/formalization.yaml` describes PaperA's formalization; its `related_formalizations`
  names the sibling papers' entries in the same repository (with `relationship: other` and a note),
  and its `sources` cite the sibling papers it uses as `background`;
- one preflight workflow per paper (`.github/workflows/palomar_preflight_papera.yml`), whose
  `options` give both paths:
  `{"comparator_config_path":"palomar/PaperA/comparator.json","formalization_metadata_path":"palomar/PaperA/formalization.yaml","authorization_relationship":"…"}`;
- run Palomar's local checks once per paper, with the metadata path of that paper; the source
  checks cover the whole repository.

Each submission is reviewed and registered on its own, so each needs the user's permission on its
own (SKILL.md, Rules).

Palomar reviews a commit of the whole repository. Its source checks read every `.lean` file (the
module header, at most 10,000 lines, no symbolic links), so a paper still in progress must meet
them too; its `sorry`s do not fail them. But they fail the shared audit, and so the CI of the
finished papers: keep the default branch building and audited, and develop a new paper on a branch
until its proofs are done (its statements, once checked, are that branch's baseline). A paper already registered stays pinned to the commit
it was submitted at: moving it to the multi-paper layout does not change that entry, and whether to
resubmit it from the new layout is the user's decision.

## 8. Tools

- `sync_challenge_defs.py`: one `(definitions module, Challenge)` pair per paper in `PAIRS`
  (`('<Project>/PaperA/Defs.lean', 'palomar/PaperA/Challenge.lean')`); `--check` checks every pair.
- `linkify_docs.py`: every paper's documents and the umbrella README in `DOCS`; in
  `NAMESPACES_BY_DIR`, each paper's document directory with its namespaces, the library's first and
  then the Challenge's (`{'docs/PaperA': ['PaperA', 'PaperAChallenge'], …}`), so that a short name
  in a paper's documents links to that paper's declaration; `MODULE_ROOTS`: `<Project>` and the
  papers' Challenge roots; `SOURCE_DIRS`: `{'PaperA': 'palomar', …}`, since the Challenge and
  Solution modules live in `palomar/`; `PREFERRED_MODULE`: a tuple of every paper's Challenge, so
  that a definition links to the Challenge's copy. Links are relative to each document's
  directory. A short name of fewer than four characters is never looked up (it reads as a
  variable): write it qualified (`PaperA.jac`).
- `check_md_tables.py`: run it on every document.
- CI (`assets/lean_action_ci.yml`): run the sync check, the route check (once per paper), the links
  and the tables for every paper.

## 9. Adding a paper to an existing repository

When a repository that holds one paper in the single-paper layout receives a second one:

1. Move to the layout of Section 2 before the second paper's statements are written, with `git mv`
   so that history follows the files: `PaperName/` to `<Project>/PaperA/` (its modules become
   `<Project>.PaperA.…`; rename its namespace after the paper if it was named after the subject,
   and its Challenge namespace too), `Basic/` and `External/` to `<Project>/Common/`, its Challenge,
   Solution, `comparator.json` and `formalization.yaml` to `palomar/PaperA/`, and its README,
   REPORT, CREDITS, routes and `NEXT.md` to `docs/PaperA/`. Point the tools at the new paths (the
   lakefile, the audit's imports and `isLibraryModule`, CI, `PAIRS`, the link configuration, the
   preflight workflow). Ignore `NEXT.md` in every directory (`NEXT.md` in `.gitignore`, without a
   leading slash). Rewrite every relative link of the moved documents: resolve it against the
   document's old directory, map the target to its new path, and make it relative to the new
   directory; then rerun `linkify_docs.py`.
2. Split any definitions that the second paper also needs into that paper's own definitions module
   (Section 3); do not let the first paper's Challenge grow definitions it does not use.
3. Rebuild, and rerun every check of Phase 6 for the first paper (audit, route check, Comparator,
   Palomar's local checks), and `scripts/stmt_diff.py` against the commit before the move: the move
   must change no statement and no proof's route, apart from the renames.
4. Write the umbrella README, and turn the first paper's README into a paper README that links to
   it.
5. Commit the move on its own, with a message that lists the renames, before any new mathematics.
   A branch that already holds work on the new paper takes the move by a merge: git places most
   moved files by its rename detection, but files the branch added in a moved directory need to be
   moved by hand, and their imports rewritten.
