# formalize-math-paper

An [Agent Skill](https://agentskills.io) for formalizing a mathematics research paper in Lean 4
with Mathlib, in any area of mathematics. It works with any agent that supports the `SKILL.md`
format: Claude Code, OpenAI Codex, Gemini CLI, Google Antigravity, GitHub Copilot, Cursor,
OpenCode, Amp and others.

It takes a paper (an arXiv link is enough), or an existing Lean draft that has never compiled, to
a Lean project that builds with no `sorry` and no `axiom`, with an audit of the paper and the
files to submit it to the [Palomar](https://palomar-registry.org) registry.

| Step | What the skill does |
| --- | --- |
| Inventory | records the paper's results, constants, citations and suspected typos |
| Project | sets up a Lean project on a Mathlib release, with the module system, in the standard layout (below), with three layers: `Basic/` (general mathematics, for later contribution to Mathlib), `External/` (the results the paper cites, in their sources' terms) and the paper's own library |
| Statements | states every result first, and checks each statement against the paper's TeX source |
| Proofs | proves what the paper proves, by the paper's own arguments, then the results it cites. A proof departs from the paper's only when it must (an error in the paper, or a representation Lean forces), never because Lean lacks the mathematics: the skill builds the missing theory, in a Lake package of its own when it is general, and tells you its estimate. Every departure is reported to you with its reason |
| Verification | checks the axioms of every declaration, checks that each proof uses the results that the paper's proof cites (extracted from the TeX source), and runs Comparator |
| Cleanup | removes unused hypotheses and other warnings without changing any proof's argument |
| Documents | writes a short `README.md`, and, in `docs/PaperName/`, `REPORT.md` (errors and gaps, missing and redundant hypotheses, use of cited results, departures, the paper in the literature, what comes next) and `CREDITS.md` (how the formalization was made, from a run log) |
| Next papers | writes a private `NEXT.md`, kept out of git: directions that would each make a paper of their own, explored to the step where the paper's method stops and checked for novelty |
| Packaging | prepares the Challenge/Solution pair, `comparator.json` and `formalization.yaml` for Palomar, and, with your permission, publishes the project and runs Palomar's preflight |

A project with one paper ([`references/lean-project.md`](references/lean-project.md), Section 2)
has its Lean code under one root named after the paper, `PaperName/`, with `Basic/`, `External/`
and the paper's sections; its Palomar submission in `palomar/PaperName/`; its documents in
`docs/PaperName/`; the README and the licence at the root. A related paper (a sequel, the other
case of one problem, a refutation) can join the repository later. The first paper's code then moves
once, under a root named after the project, with the shared code in `ProjectName/Common/` and one
directory per paper ([`references/multi-paper.md`](references/multi-paper.md)); the Palomar files
and the documents stay. The papers share code, each keeps its own Challenge, Palomar submission and
documents, and an umbrella README connects them.

## Made with this skill

| Repository | What it formalizes |
| --- | --- |
| [lean4-smoothed-polygon](https://github.com/vltanh/lean4-smoothed-polygon) | Hales and Vajjha, *Packings of Smoothed Polygons* (arXiv:2405.04331): Chapters 2–8, with an audit of the book (61 findings, among them false statements refuted in Lean); Mahler's First conjecture (Theorem 16.3.1) proved conditionally on one named hypothesis |
| [lean4-morrey](https://github.com/vltanh/lean4-morrey) | three papers on Morrey's problem in one repository: Šverák's counterexample on `ℝ^{3×2}` (1992) and Cassese's on `ℝ^{2×m}`, `m ≥ 3` (arXiv:2608.03488; every result, a few conditional on named hypotheses), and an audit of Pedregal's claimed proof for `2 × 2` (arXiv:1905.06571), whose Corollary 7.2 is refuted in Lean |
| [lean4-optimal-control](https://github.com/vltanh/lean4-optimal-control) | the Pontryagin maximum principle by Agrachev and Sachkov's proof, and Filippov's theorem, including the form with a state constraint |
| [lean4-fixed-point](https://github.com/vltanh/lean4-fixed-point) | Brouwer's fixed-point theorem, by the analytic proof of Milnor and Rogers |

## Install

With the [`skills`](https://github.com/vercel-labs/skills) installer, which detects your agents
and links the skill into each of them:

```sh
npx skills add vltanh/formalize-math-paper -g      # for your user; omit -g to install into the current project
```

The installer puts the skill in `~/.agents/skills/`, which most agents read, and links it into
the directories of the agents that do not. Antigravity reads user-wide skills only from
`~/.gemini/config/skills/`, so link it there too:

```sh
mkdir -p ~/.gemini/config/skills && ln -s ~/.agents/skills/formalize-math-paper ~/.gemini/config/skills/
```

Or copy the repository into your agent's skills directory by hand:

```sh
git clone https://github.com/vltanh/formalize-math-paper <skills-dir>/formalize-math-paper
```

| Agent | User skills directory | Project skills directory |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/` | `.claude/skills/` |
| OpenAI Codex | `~/.agents/skills/` (older versions: `~/.codex/skills/`) | `.agents/skills/` |
| Gemini CLI | `~/.gemini/skills/` or `~/.agents/skills/` | `.gemini/skills/` or `.agents/skills/` |
| Google Antigravity | `~/.gemini/config/skills/` | `.agents/skills/` |
| GitHub Copilot (VS Code) | `~/.copilot/skills/`, `~/.agents/skills/` or `~/.claude/skills/` | `.github/skills/`, `.agents/skills/` or `.claude/skills/` |
| Cursor | `~/.cursor/skills/` or `~/.agents/skills/` | `.cursor/skills/` or `.agents/skills/` |
| Other agents | their skills directory; many read `~/.agents/skills/` | `.agents/skills/` |

Start a new session afterwards. The agent then uses the skill when you ask it to formalize a
paper (an arXiv link is enough), to make a Lean draft compile, or to prepare a Lean project for
Palomar. In Codex you can also invoke it as `$formalize-math-paper`.

An agent without skill support can still follow it. Add a line such as "To formalize a
mathematics paper in Lean, follow `~/.agents/skills/formalize-math-paper/SKILL.md`" to its
instructions file (`AGENTS.md` or the equivalent), or say so in your request.

## Requirements

A shell, git, Python 3, and a Lean 4 toolchain ([elan](https://github.com/leanprover/elan)). The
GitHub CLI and [bubblewrap](https://github.com/containers/bubblewrap) are needed to publish and to
run Comparator locally. Agents that can run sub-agents in parallel finish large formalizations
faster, but they are not required.

## Contents

| Path | Contents |
| --- | --- |
| `SKILL.md` | The workflow: principles, rules, phases and completion gates |
| `references/` | Detailed guides: Lean project setup, parallel repair, the audit report, follow-up papers, the credits, Palomar packaging, cleanup, rigorous numerics, packages of their own for the theory that Lean lacks, several papers in one repository, checklists (statement review, verification, status reports, completion gates), the bundled tools |
| `scripts/` | Helpers: checking one file, against the build or a private snapshot of it; replacing failing proofs with `sorry`; converting to the module system; statement diffs; removing unused hypotheses and the arguments that callers pass for them; checking that each proof follows the route of the paper's proof; copying shared definitions into the Challenge; linking documentation to the code; checking Markdown tables; summarizing a Claude Code session for the run log |
| `assets/` | Templates: the axiom, dependency and route audit (`Audit.lean`), the CI workflow, the Palomar preflight workflow |

## License

Apache-2.0; see [LICENSE](LICENSE).
