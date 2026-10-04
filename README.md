# formalize-math-paper

An [Agent Skill](https://agentskills.io) for formalizing a mathematics research paper in Lean 4
with Mathlib, in any area of mathematics. It works with any agent that supports the `SKILL.md`
format: Claude Code, OpenAI Codex, Gemini CLI, Google Antigravity, GitHub Copilot, Cursor,
OpenCode, Amp and others.

The skill guides the work from start to finish:

- read the paper and record its results, constants, citations and suspected typos;
- set up a Lean project on a Mathlib release, using the module system;
- state every result first, and check each statement against the paper's TeX source;
- prove everything the paper proves (Stage 1), by the paper's own arguments, then every result it
  cites (Stage 2), until the project has no `sorry` and no `axiom`. A proof departs from the
  paper's only when it must: the paper's step is wrong, needs mathematics that Lean lacks, or has
  no meaning in the formalization's representation. Every departure is reported, with its reason,
  in the code, the report, the metadata and to you. A cited result that no Lean library can
  yet support becomes a visible hypothesis of the statements that use it, and the result is
  reported as conditional. The skill asks you only when building the missing theory would be a
  large but feasible effort;
- verify: the axioms of every declaration; the route of every proof (the paper's results it
  uses) against the results that the paper's proof cites, extracted from the TeX source; and
  Comparator;
- clean up: remove unused hypotheses and other warnings, without changing any proof's argument;
- write `REPORT.md`, an audit of the paper against the formalization (errors and gaps, missing
  and redundant hypotheses, how the paper uses each cited result, every departure from the
  paper's proofs) that ends with what comes next: the work that has followed the paper, ways to
  extend, generalize or strengthen its results, and where its proofs could be simpler; and a short
  `README.md`;
- package the project for the [Palomar](https://palomar-registry.org) registry by default
  (Challenge/Solution, `comparator.json`, `formalization.yaml`), and, with your permission,
  publish it and run Palomar's preflight;
- keep a run log, and report in `CREDITS.md` how the formalization was made: the procedure, the
  agents and models, the elapsed time and the effort.

It also covers turning an existing, never-compiled Lean draft into a project that builds.

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
| `references/` | Detailed guides: Lean project setup, parallel repair, the audit report, the credits, Palomar packaging, cleanup, rigorous numerics |
| `scripts/` | Helpers: checking one file, against the build or a private snapshot of it; replacing failing proofs with `sorry`; converting to the module system; statement diffs; removing unused hypotheses and the arguments that callers pass for them; checking that each proof follows the route of the paper's proof; copying shared definitions into the Challenge; linking documentation to the code; checking Markdown tables; summarizing a Claude Code session for the run log |
| `assets/` | Templates: the axiom, dependency and route audit (`Audit.lean`), the CI workflow, the Palomar preflight workflow |

## License

Apache-2.0; see [LICENSE](LICENSE).
