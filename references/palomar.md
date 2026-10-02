# Packaging for Palomar

Palomar (https://palomar-registry.org) is a registry of machine-checked Lean proofs. A submission
is an exact commit of a public GitHub repository together with a Challenge/Solution pair. The
Challenge states the result. Comparator checks that the Solution proves exactly the Challenge's
statements, using only the permitted axioms, under Lean's kernel and independent kernels
(NanoDa, con-ron). An AI editorial review then compares the formal statements with their
informal descriptions.

The rules change. Before packaging, read the current versions:

- the policy: https://github.com/PalomarRegistry/PalomarPolicy (`CONTRIBUTING.md`);
- the verifier: https://github.com/PalomarRegistry/PalomarSubmission (`README.md`; templates
  in `tests/fixtures/`; taxonomies in `taxonomies/`);
- the agent instructions: https://submit.palomar-registry.org/llms.txt.

Clone the two repositories to a scratch directory. Their scripts validate the metadata and
sources locally.

Package every project for Palomar unless the user declined (SKILL.md, Phase 0): the files and the
local checks need no permission, and they make the project ready to submit when the user decides
to.

## Contents

1. Repository requirements
2. Challenge and Solution
3. `comparator.json`
4. `formalization.yaml`
5. Local checks
6. CI
7. The preflight
8. Publishing and submitting

## 1. Repository requirements

- `lean-toolchain` names a Lean release, no older than the minimum in PalomarSubmission's
  `toolchains.json`, and identical to the pinned Mathlib commit's `lean-toolchain`.
- `lakefile.toml` (or `lakefile.lean`) and `lake-manifest.json` are committed. Dependencies are
  public GitHub repositories pinned to full commit hashes; the manifest provides the pins.
  Mathlib's pinned commit must be on Mathlib's `master` branch: check it with
  `gh api repos/leanprover-community/mathlib4/compare/<sha>...master --jq .status`, which should
  print `ahead` or `identical`.
- Every `.lean` file, scripts and unused files included, uses the module system and has at most
  10,000 lines. The Challenge has at most 1,000 lines and 100 KiB, and over 300 lines or 32 KiB it
  draws a warning. Template fragments that generators assemble are not modules: name them
  `*.lean.in`.
- Exactly one license file at the root, containing the standard SPDX text, matching
  `project.license`. Apache-2.0 is the common choice; copy the unmodified text.
- No build outputs, no Git submodules, no Git LFS.

## 2. Challenge and Solution

- `Challenge.lean` contains only the statements of record, with `sorry` proofs, in Mathlib's
  vocabulary: no imports from the project. Restate project definitions inline with Mathlib
  constructions; for example, a probability over a finite set becomes a count divided by a
  cardinality. Write the module docstring as a plain-language account of each theorem, with
  every convention it uses. State the results exactly as the paper does, quantifiers and
  constants included.
- The solution module repeats each Challenge theorem verbatim, with the same names and types, and
  proves it from the development. Bridge lemmas translate between the project's definitions and
  the Challenge's vocabulary. `Solution.lean` can import the whole development and serve as the
  project's entry point.
- Put both in the lakefile: `Challenge` and `Solution` as `lean_lib`s and default targets.
- When the Challenge defines an object a reader cannot recognize at a glance, include a compared
  theorem that identifies it with the literature, such as its known numerical value. The
  editorial review checks that every definition has its ordinary meaning, and such a theorem is
  the evidence.

## 3. `comparator.json`

```json
{
  "challenge_module": "Challenge",
  "solution_module": "Solution",
  "theorem_names": ["PaperNamespace.theorem_1_1", "PaperNamespace.theorem_1_2"],
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
- `project.description` is the public abstract: the subject and the principal results, for a
  mathematically literate reader.
- `classification.arxiv` takes 1–8 codes and `classification.msc2020` up to 8. Each must exist in
  PalomarSubmission's `taxonomies/arxiv-categories.json` or `taxonomies/msc2020-codes.json`.
  Check them.
- `sources`: the paper with `relationship: formalizes`, and with `author_endorsement:
  not-contacted` unless the authors were contacted. Cited works that the formalization proves go
  under `background`, with a note.
- `related_formalizations`: earlier, independent formalizations, as found in Phase 0, each with
  `relationship: independent` (or another honest value) and a note saying whether this work
  consulted it. A superseded draft of this same project does not belong here. Palomar does not
  index "duplicated or lightly repackaged work without useful provenance": if the result is
  already formalized, say so plainly, and tell the user before submission.
- `automation`: fill it from the run log (SKILL.md): the model(s), the framework and harness with
  their versions, `tool_setup` naming the procedure (this skill, with its repository and commit)
  and the number of agents, `cost.wall_time` with the elapsed time and the total agent time, and
  `spend_usd` if known, otherwise "not tracked".
- `status`: `sorry_count: 0`, `sorry_in_definitions: 0`, `axioms: []`. `scope` says exactly what
  is and is not formalized.
- `fidelity.divergences`: every reading or deviation from the paper. They must agree with the
  report.
- `review.status`: honest. `agent-reviewed` if only AI systems reviewed it; never imply a human
  review that did not happen.
- The README carries the literature account the review checks: the history of the problem, the
  sources, and the earlier formalizations. For a famous problem, Palomar also expects a careful
  comparison of the Challenge with the standard formulation of the problem.
- `alignment.statements`: one entry for each Comparator theorem, giving its source, Lean name,
  module and status.

## 5. Local checks

```sh
# Palomar's metadata and source checks (from a clone of PalomarSubmission). Point R at a clean
# clone of the project (`git clone <project> /tmp/check`), so that untracked files in your working
# directory, such as notes, do not count:
python3 -c "
import sys; sys.path.insert(0, '.')
from pathlib import Path
from scripts import submission_contract as sc, source_requirements as sr
R = Path('/path/to/project')
sc.load_formalization_metadata(R / 'formalization.yaml'); print('metadata OK')
summary, issues = sr.inspect_lean_sources(R); print(summary['files_checked'], 'files', issues)"

# Comparator, in a bubblewrap sandbox (Lake's built-in command). If NanoDa is not installed
# locally, run a copy of the configuration with NanoDa disabled; Palomar supplies NanoDa itself.
sed 's/"enable_nanoda": true/"enable_nanoda": false/' comparator.json > /tmp/comparator-local.json
lake comparator --config=/tmp/comparator-local.json     # expect "Your solution is okay!"
```

The licence detector is the `licensee` gem. A byte-for-byte copy of Mathlib's `LICENSE` is
detected as Apache-2.0. After publishing, `gh api repos/<owner>/<name>/license --jq .license.spdx_id`
shows what GitHub detects; it may take a minute after the first push.

## 6. CI

`assets/lean_action_ci.yml` builds the project on every push, runs the axiom audit, and checks
that the documentation's links are current. The Lake `math` template's documentation workflow
(`docs.yml`, using `docgen-action`) generates documentation for every imported module, all of
Mathlib included. It runs for hours on a GitHub runner and typically fails, so leave it out
unless the user wants API documentation and accepts the cost.

## 7. The preflight

Palomar asks that you run its complete verification workflow on the exact commit before
submitting, and submit only when the report says `status: pass`.

1. Copy `assets/palomar_preflight.yml` to `.github/workflows/`. Pin both the `uses:` reference
   and `pipeline_commit` to the same full PalomarSubmission commit
   (`git ls-remote https://github.com/PalomarRegistry/PalomarSubmission.git HEAD`). `request_id`
   must be exactly 12 lowercase letters or digits.
2. The verifier fetches the repository anonymously, so the repository must be public. Ask the
   user before making it public. The workflow's `options` declare the authorization relationship,
   which the public report records: check with the user that it is accurate.
3. Run it on the commit to submit (`gh workflow run palomar_preflight.yml --ref main`). If you push
   again, run it again: the submitted commit must be the one that passed.
4. Download the report and read it:

   ```sh
   gh run download <run-id> -n mechanical-report-preflight001 -D /tmp/preflight
   python3 -c "import json; d = json.load(open('/tmp/preflight/mechanical-report.json')); print(d['status'], d['errors'], d['warnings'])"
   ```

   Only `status: pass` counts. If it is anything else, read `errors`, `build_log_tail` and
   `comparator_log_tail`, fix the problem, push, and run the preflight again.

## 8. Publishing and submitting

After the repository is created, add the CI badge to the top of the README.

Each of these steps needs the user's explicit permission: creating the GitHub repository, pushing,
making it public, submitting, registering. Permission for one is not permission for another.

Submissions go to https://submit.palomar-registry.org only. Before submitting, show the user:

- the repository (`owner/name`);
- the full 40-character commit (the one that passed the preflight);
- the Comparator configuration path (`comparator.json`);
- the authorization relationship. This is a claim about the user ("I am a responsible author or
  maintainer"), and Palomar records it permanently.

Then offer the two ways to submit:

- **The browser** (the user signs in with GitHub). This is the stronger proof of who submitted.
- **The `gh` route described in `llms.txt`** (intake, a temporary tag, a secret gist, verify,
  then delete both). Palomar records that this route proves less than the browser sign-in: tell
  the user that it is not equivalent. Never drive the browser sign-in yourself.

After submission, Palomar verifies again and runs its editorial review. Treat the access token as
a credential, and do not post the review publicly. Registration publishes the review and is
permanent. Show the user the review and what registering would publish, and register only when
they decide to.
