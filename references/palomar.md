# Packaging for Palomar

Palomar (https://palomar-registry.org) is a registry of machine-checked Lean proofs. A submission
is an exact commit of a public GitHub repository, with a Challenge/Solution pair. The Challenge
states the result. Comparator checks that the Solution proves exactly the Challenge's statements,
using only the permitted axioms, under Lean's kernel and under independent kernels (NanoDa,
con-ron). Then an AI editorial review compares the formal statements with their informal
descriptions.

The rules change. Before you package, read the current versions:

- the policy: https://github.com/PalomarRegistry/PalomarPolicy (`CONTRIBUTING.md`);
- the verifier: https://github.com/PalomarRegistry/PalomarSubmission (`README.md`; templates
  in `tests/fixtures/`; taxonomies in `taxonomies/`);
- the agent instructions: https://submit.palomar-registry.org/llms.txt.

Clone the two repositories to a scratch directory. Their scripts check the metadata and sources
locally.

Package every project for Palomar unless the user declined (SKILL.md, Phase 0). The files and the
local checks need no permission, and they make the project ready to submit whenever the user
decides to.

## Contents

1. Repository requirements
2. Challenge and Solution
3. `comparator.json`
4. `formalization.yaml`
5. Local checks
6. CI
7. Publishing
8. The preflight
9. Submitting and registering

## 1. Repository requirements

- `lean-toolchain` names a Lean release, no older than the minimum in PalomarSubmission's
  `toolchains.json`, and identical to the pinned Mathlib commit's `lean-toolchain`.
- `lakefile.toml` (or `lakefile.lean`) and `lake-manifest.json` are committed. Dependencies are
  public GitHub repositories pinned to full commit hashes; the manifest provides the pins.
  Mathlib must be pinned to a commit on its `master` branch or to an exact release tag. Use the
  release tag for the toolchain, because of the next point.
- Everything that the Challenge imports, directly or indirectly, must come from Lean core, Mathlib
  or Tau Ceti, at pins on Palomar's allowlist, and from nothing else. Importing Tau Ceti is
  allowed, but it marks the entry as having qualified statement dependencies. A project that
  Palomar has registered cannot be imported. Dependencies used only by the Solution may be any
  public Git repository pinned to a commit. A library that tracks Mathlib's `master`, as Tau Ceti
  does, requires a specific Mathlib commit: use the commit its manifest pins, and compare the
  resulting manifest with Verso's, as below.
- The Challenge must render. After verification, Palomar renders it with the release of Verso
  (Lean's documentation tool) for the project's toolchain, and merges Verso's Lake manifest into
  the project's. If both pin a package at different revisions, the render stops, and the
  submission stalls at the Challenge renderability check. The preflight does not render, so
  compare the pins yourself: every package that appears both in `lake-manifest.json` and in
  Verso's manifest for the toolchain's tag must have the same `rev`.

  ```sh
  gh api 'repos/leanprover/verso/contents/lake-manifest.json?ref=<toolchain tag>' --jq .content | base64 -d
  ```

  Mathlib's release tag for the toolchain usually pins the same revisions as Verso; a later
  `master` commit soon does not. Moving Mathlib to the tag means rebuilding and rechecking
  everything. When a dependency forces a `master` commit, compare anyway: on the same toolchain,
  the shared packages often still match.
- Every `.lean` file, including scripts and unused files, uses the module system and has at most
  10,000 lines. The Challenge has at most 1,000 lines and 100 KiB, and gets a warning above 300
  lines or 32 KiB. Template fragments that generators assemble are not modules: name them
  `*.lean.in`.
- Exactly one license file at the root, with the standard SPDX text, matching `project.license`.
  Apache-2.0 is the common choice; copy the text unchanged.
- No build outputs, no Git submodules, no Git LFS.

## 2. Challenge and Solution

- `Challenge.lean` contains only the statements of record, which are the paper's main results,
  with `sorry` proofs, in Mathlib's vocabulary. It imports nothing from the project. Use Tau Ceti's
  vocabulary only when restating its definitions would cost more than the qualified mark (Section
  1). Restate project definitions inline with Mathlib constructions. For example, a probability
  over a finite set becomes a count divided by a cardinality. Write the module docstring as a
  plain-language account of each theorem, with every convention it uses. State the results exactly
  as the paper does, including quantifiers and constants, except for obvious misprints, which are
  corrected and documented (SKILL.md, Rules).
- A conditional result states each assumed result as a hypothesis, never as an axiom. Several may
  be bundled in a class of hypotheses, named for what it is. Write the class in the signature of
  each theorem that needs it. Do not declare it with `variable`, which hides which theorems use it.
  Keep data and assumptions apart: the class takes the data as parameters. The module docstring
  lists the assumed results, with their sources.
- When the statements need definitions too large to restate inline, keep them in one
  module of the library, between two marker comments. Copy that block word for word into the
  Challenge with `scripts/sync_challenge_defs.py`; CI runs it with `--check`. Comparator requires
  the constants that the statements use to be the same in the Challenge and in the Solution's
  environment, and the exact copy makes them the same without bridge lemmas. Put the Challenge's
  theorems in a namespace of their own. Then the Solution, which imports the library, can restate
  them without clashing with the library's names.
- The solution module repeats each Challenge theorem word for word, with the same names and types,
  and proves it from the rest of the project. Bridge lemmas translate between the project's
  definitions and the Challenge's vocabulary. `Solution.lean` can import the whole project and
  serve as its entry point.
- Put both in the lakefile: `Challenge` and `Solution` as `lean_lib`s and default targets.
- When the Challenge defines an object a reader cannot recognize at a glance, include a
  compared theorem that identifies it with the literature, such as its known numerical value. The
  editorial review checks that every definition has its ordinary meaning, and such a theorem is the
  evidence.

## 3. `comparator.json`

```json
{
  "challenge_module": "Challenge",
  "solution_module": "Solution",
  "theorem_names": ["PaperNamespace.theorem1_1", "PaperNamespace.theorem1_2"],
  "definition_names": [],
  "permitted_axioms": ["propext", "Quot.sound", "Classical.choice"],
  "enable_nanoda": true
}
```

## 4. `formalization.yaml`

Start from the current template, `tests/fixtures/palomar-template-formalization.yaml` in
PalomarSubmission (format v0.4), and replace every `TEMPLATE` value. The rules that matter most:

- `project.authors` and `project.responsible_maintainers` are people only: the user, or whoever
  they name. Credit AI systems in `automation.methods`, one entry per system, with `method:
  agent` (or `manual`, `copilot`, `autonomous`, `other`), `models`, `framework`, `tool_setup`,
  and costs, or "not tracked".
- `project.description` is the public abstract: the subject and the main results, for a reader
  who knows mathematics. Keep it short, and state what is proved. Palomar shows it as plain text
  that keeps line breaks. Separate paragraphs with an empty line, which a folded block (`>-`)
  writes as two empty lines.
- `classification.arxiv` takes 1–8 codes and `classification.msc2020` up to 8. Each must exist in
  PalomarSubmission's `taxonomies/arxiv-categories.json` or `taxonomies/msc2020-codes.json`.
  Check them.
- `sources`: the paper with `relationship: formalizes`, and with `author_endorsement:
  not-contacted` unless the authors were contacted. Cited works that the formalization proves go
  under `background`, with a note; so do cited works that it assumes, with a note that says so. A
  source of `type: original-proof` declares that the formalization is where its result first
  appears, and Palomar then requires every source to be `background` or `other`. A project that
  formalizes a paper and adds a new result keeps the paper as `formalizes`, and records the
  document of the new argument with `type: other`, its location pinned to a commit.
- `related_formalizations`: earlier, independent formalizations, as found in Phase 0, each with
  `relationship: independent` (or another honest value) and a note that says whether this work
  consulted it. An old draft of this same project does not belong here. Palomar does not index
  "duplicated or lightly repackaged work without useful provenance": if the result is already
  formalized, say so plainly, and tell the user before submission.
- `automation`: fill it from the run log (SKILL.md): the model(s), the framework and harness with
  their versions, `tool_setup` naming the procedure (this skill, with its repository and commit) and
  the number of agents, `cost.wall_time` with the elapsed time and the total agent time, and
  `spend_usd` if known, otherwise "not tracked". The figures must agree with `CREDITS.md`.
- `status`: `sorry_count: 0`, `sorry_in_definitions: 0`, `axioms: []`. `scope` says exactly what
  is and is not formalized. A conditional formalization says so at the start of `scope` and of
  `project.description`, and names the assumed results; `fidelity.divergences` lists them.
- `fidelity.divergences`: every reading of the paper and every deviation from it, in the
  statements and in the proofs: the corrections of statements, the readings, and every departure
  from the paper's proofs with its reason (or a sentence saying that every proof follows the
  paper's). They must agree with the report.
- `review.status`: honest. `agent-reviewed` if only AI systems reviewed it; never imply a human
  review that did not happen.
- `alignment.statements`: one entry for each Comparator theorem, giving its source, Lean name,
  module and status.

The editorial review also reads the README, which gives the account of the literature: the
history of the problem, the sources, and the earlier formalizations. For a well-known problem,
Palomar also expects a careful comparison of the Challenge with the standard formulation of the
problem.

## 5. Local checks

Run Palomar's metadata and source checks from a clone of PalomarSubmission. Point `R` at a fresh
clone of the project (`git clone <project> <scratch dir>/check`), so that untracked files in your
working directory, such as notes, do not count:

```sh
python3 -c "
import sys; sys.path.insert(0, '.')
from pathlib import Path
from scripts import submission_contract as sc, source_requirements as sr
R = Path('<scratch dir>/check')
sc.load_formalization_metadata(R / 'formalization.yaml'); print('metadata OK')
summary, issues = sr.inspect_lean_sources(R); print(summary['files_checked'], 'files', issues)"
```

Run Comparator from the project root, in a bubblewrap sandbox (Lake's built-in command). `lake env`
puts the toolchain's `bin/` directory, which holds the NanoDa kernel (`nanoda_bin`), on the path:

```sh
lake env lake comparator --config=comparator.json    # expect "Your solution is okay!"
```

If the toolchain has no `nanoda_bin`, run a copy of the configuration with
`"enable_nanoda": false`. Palomar runs its independent kernels (NanoDa and con-ron) whatever the
file says.

## 6. CI

`assets/lean_action_ci.yml` builds the project on every push, runs the axiom audit, and checks
that the Challenge's copy of the shared definitions (if any) and the documentation's links and
tables are up to date. The CI workflow of the Lake `math` template also generates API documentation
for every imported module, including Mathlib, which can take hours. Use the asset instead, unless
the user wants that documentation.

## 7. Publishing

Each of these steps needs the user's explicit permission: creating the GitHub repository, pushing,
making it public, running the preflight, submitting, registering. Permission for one is not
permission for another.

- After the repository is created, add the CI badge to the top of the README, before the commit
  that will go through the preflight and be submitted.
- The verifier fetches the repository anonymously, so the repository must be public before the
  preflight.
- Palomar and GitHub detect the license with the `licensee` gem, which recognizes only the
  standard text. After the first push, `gh api repos/<owner>/<name>/license --jq .license.spdx_id`
  shows what GitHub detects.

## 8. The preflight

Palomar asks you to run its full verification workflow on the exact commit before you submit, and
to submit only when the report says `status: pass`. The preflight does not render the Challenge or
run the editorial review (Section 1).

1. Copy `assets/palomar_preflight.yml` to `.github/workflows/`. Pin both the `uses:` reference
   and `pipeline_commit` to the same full PalomarSubmission commit
   (`git ls-remote https://github.com/PalomarRegistry/PalomarSubmission.git HEAD`). `request_id`
   must be exactly 12 lowercase letters or digits.
2. The workflow's `options` declare the authorization relationship, which the public report
   records. Check with the user that it is accurate, and ask before running the workflow.
3. Run it on the commit to submit (`gh workflow run palomar_preflight.yml --ref main`). If you push
   again, run it again: the submitted commit must be the one that passed.
4. Download the report, whose artifact is named after the `request_id`, and read it:

   ```sh
   gh run download <run-id> -n mechanical-report-preflight001 -D <scratch dir>/preflight
   python3 -c "import json, sys; d = json.load(open(sys.argv[1])); print(d['status'], d['errors'], d['warnings'])" <scratch dir>/preflight/mechanical-report.json
   ```

   Only `status: pass` counts. If it is anything else, read `errors`, `build_log_tail` and
   `comparator_log_tail`, and fix the problem. Then, with the user's permission, push and run
   the preflight again.

## 9. Submitting and registering

Submissions go to https://submit.palomar-registry.org only. Before submitting, show the user:

- the repository (`owner/name`);
- the full 40-character commit (the one that passed the preflight);
- the path of the Comparator configuration (`comparator.json`);
- the authorization relationship. This is a claim about the user ("I am a responsible author or
  maintainer"), and Palomar records it permanently.

Then offer the two ways to submit:

- **The browser** (the user signs in with GitHub). This gives the stronger proof of who submitted.
- **The `gh` route described in `llms.txt`** (intake, a temporary tag, a secret gist, verify,
  then delete both). Palomar records that this route proves less than the browser sign-in: tell
  the user that the two are not equivalent. Never drive the browser sign-in yourself.

After submission, Palomar verifies again, renders the Challenge, and runs its editorial review.
Follow it on the status page, or with `GET /api/submission` and the access token, as described in
`llms.txt`. When a submission stays at the Challenge renderability check, check the pins of
Section 1: a conflict there does not go away if you retry. Fix it, and, with the user's
permission, submit the corrected commit as a new submission. Treat the access token as a secret,
and do not post the review publicly. Registering publishes the review and is permanent. Show the
user the review and what registering would publish, and register only when they decide to.
