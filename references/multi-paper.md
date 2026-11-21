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

```text
README.md              -- the umbrella document (Section 6)
LICENSE                -- once, at the root (Palomar reads only the root licence)
lakefile.toml, lean-toolchain, lake-manifest.json
.github/workflows/     -- CI for every paper; one preflight workflow per paper
scripts/               -- the shared tools, configured for every paper (Section 8)
Basic/                 -- general mathematics, shared
External/              -- cited results, shared: a result two papers cite is formalized once
PaperA/                -- one directory per paper, named after it (first author, or a short title)
  Defs.lean            -- every definition PaperA's Challenge uses, self-contained (Section 3)
  Challenge.lean       -- module PaperA.Challenge
  Solution.lean        -- module PaperA.Solution, PaperA's entry point
  …                    -- PaperA's library, by section as for a single paper
  comparator.json, formalization.yaml
  README.md, REPORT.md, CREDITS.md
  docs/paper_routes.tsv, docs/route_differences.tsv
  NEXT.md              -- private, ignored by git (Phase 8)
PaperB/                -- the same
```

Each paper's directory is a `lean_lib` of its own (`globs = ["PaperA.+"]`), with its own
namespace. Name the directory and the namespace after the paper, not after the subject: the
subject is the repository's, and two papers on one subject need different names.

Decide the layout before the second paper's statements are written. Moving a paper's files later
rewrites module names, namespaces, the audit's list of modules, the routes, every document's links
and the Palomar files, and conflicts with any branch that touches them (Section 9).

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
  shared library (for example `Common/`) imported by neither paper's Challenge.
- `Basic/` and `External/` stay shared and keep their layering: `Basic` imports only Mathlib,
  `External` only Mathlib and `Basic`, and no paper library is imported by them.

## 5. Routes, audit and findings

- Each paper has its own `docs/paper_routes.tsv` and `docs/route_differences.tsv` in its directory.
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
  `find Basic External PaperA PaperB -name '*.lean' ! -name Challenge.lean | sort | sed …`, and give
  the CI step that checks the audit's imports the same `find`. The audit lists every paper's
  numbered results (with the paper in the label: "Šverák Lemma 1") and every paper's Comparator
  theorems, sets `isLibraryModule` to every library root, and checks every declaration's axioms. It
  writes one `.lake/route_deps.tsv`; run the route check once per paper, with that paper's two
  files:
  `python3 scripts/route_check.py check PaperA/docs/paper_routes.tsv --accept PaperA/docs/route_differences.tsv`.
- Findings are numbered within each paper's report (E1, E2, … in each), so that a paper's report
  can be read, cited and submitted on its own. A finding that concerns two papers (one paper's
  claim refuted by another's theorem) appears in both reports, each with its own number and a link
  to the other.

## 6. Documents

Each paper keeps the documents of a single-paper project, in its own directory: `README.md`,
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
6. Trust (the build, the audit, Comparator, reviews), the shared code (`Basic/`, `External/`, shared
   libraries), building, and the layout.
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

- `PaperA/comparator.json` names `PaperA.Challenge` and `PaperA.Solution` and PaperA's theorems;
- `PaperA/formalization.yaml` describes PaperA's formalization; its `related_formalizations`
  names the sibling papers' entries in the same repository (with `relationship: other` and a note),
  and its `sources` cite the sibling papers it uses as `background`;
- one preflight workflow per paper (`.github/workflows/palomar_preflight_papera.yml`), whose
  `options` give both paths:
  `{"comparator_config_path":"PaperA/comparator.json","formalization_metadata_path":"PaperA/formalization.yaml","authorization_relationship":"…"}`;
- run Palomar's local checks once per paper, with the metadata path of that paper; the source
  checks cover the whole repository.

Each submission is reviewed and registered on its own, so each needs the user's permission on its
own (SKILL.md, Rules).

Palomar reviews a commit of the whole repository. Its source checks read every `.lean` file (the
module header, at most 10,000 lines, no symbolic links), so a paper still in progress must meet
them too; its `sorry`s do not fail them. But they fail the shared audit, and so the CI of the
finished papers: keep the default branch building and audited, and develop a new paper on a branch
until its proofs are done (its statements, once checked, are that branch's baseline). A paper already registered stays pinned to the commit
it was submitted at: moving it into its own directory does not change that entry, and whether to
resubmit it from the new layout is the user's decision.

## 8. Tools

- `sync_challenge_defs.py`: list one `(definitions module, Challenge)` pair per paper in its
  configuration block; `--check` checks every pair.
- `linkify_docs.py`: list every paper's documents and the umbrella README in `DOCS`; give each
  paper's directory its namespaces in `NAMESPACES_BY_DIR` (the library's and the Challenge's:
  `{'PaperA': ['PaperA', 'PaperAChallenge'], …}`), so that a short name in a paper's documents links
  to that paper's declaration, every library root in `MODULE_ROOTS`, and every paper's Challenge in
  `PREFERRED_MODULE` (a tuple), so that a definition links to the Challenge's copy; links are
  relative to each document's directory. A short name of fewer than four characters is never
  looked up (it reads as a variable): write it qualified (`PaperA.jac`).
- `check_md_tables.py`: run it on every document.
- CI (`assets/lean_action_ci.yml`): run the sync check, the route check (once per paper), the links
  and the tables for every paper.

## 9. Adding a paper to an existing repository

When a repository that holds one paper in the single-paper layout receives a second one:

1. Move the first paper into its own directory before the second paper's statements are written,
   with `git mv` so that history follows the files: rename its modules and namespace after the
   paper (and its Challenge namespace, if it is generic or named after the subject), move its
   Challenge, Solution, Palomar files, documents and routes into the directory, and point the
   tools at the new paths (the audit's imports, CI, `PAIRS`, `NAMESPACES_BY_DIR`, the preflight
   workflow). Ignore `NEXT.md` in every directory (`NEXT.md` in
   `.gitignore`, without a leading slash). In the moved documents, links to shared paths gain `../`
   (`../Basic/`, `../LICENSE`); links to the paper's own files still work.
2. Split any definitions that the second paper also needs into that paper's own definitions module
   (Section 3); do not let the first paper's Challenge grow definitions it does not use.
3. Rebuild, and rerun every check of Phase 6 for the first paper (audit, route check, Comparator,
   Palomar's local checks), and `scripts/stmt_diff.py` against the commit before the move: the move
   must change no statement and no proof's route, apart from the renames.
4. Write the umbrella README, and turn the first paper's README into a paper README that links to
   it.
5. Commit the move on its own, with a message that lists the renames, before any new mathematics.
