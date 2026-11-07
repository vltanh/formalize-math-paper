# Bundled tools

Run the scripts from the project root, as `python3 <skill-dir>/scripts/<name> …`. Copy the ones
that CI runs into the project's `scripts/` directory.

| Tool | Use |
| --- | --- |
| `scripts/check_file.py FILE [--autosorry]` | check one file with the lakefile's options; with `--autosorry`, replace failing proofs with `sorry` until the file elaborates |
| `scripts/autosorry.py FILE LOG` | the replacement step on its own, given Lean's output |
| `scripts/to_module.py FILE…` | convert files to the module system |
| `scripts/stmt_diff.py REV [PATH…]` | list the declarations whose statements or definitions changed since `REV` |
| `scripts/strip_unused.py LOG [--dry-run]` | delete the binders that the unused-variables linter reports |
| `scripts/strip_call_args.py [REV] [--dry-run]` | delete, at every call site, the arguments of binders removed since `REV` (default `HEAD`); run it once per cleanup round, right after `strip_unused.py`, with the commit that started the round |
| `scripts/snapshot_check.py take DIR` / `check DIR FILE [--emit]` | check files against a private copy of the build outputs, so that parallel agents do not break each other's imports |
| `scripts/session_stats.py [TRANSCRIPT…] [--since TIME] [--until TIME]` | the run log's figures (elapsed time, models, sub-agents, the most running at once, agent time, tokens, tool calls) from Claude Code session transcripts, for the whole run or for one round |
| `scripts/linkify_docs.py [--check]` | link the Lean names in the documents to their lines; copy it into the project and configure its first block |
| `scripts/check_md_tables.py FILE… [--fix]` | find, or fix, Markdown table rows broken by a `\|` inside a cell; copy it into the project |
| `scripts/route_check.py extract TEX…` / `check ROUTES [--accept FILE]` | record which results each of the paper's proofs cites; compare these with the routes of the formal proofs that the audit writes, and fail on any difference not recorded with its reason; copy it into the project |
| `scripts/sync_challenge_defs.py [--check]` | copy the block of shared definitions from a library module into `Challenge.lean`, or check that the copy is up to date (`references/palomar.md`, Section 2); copy it into the project and configure its first block |
| `assets/Audit.lean` | the axiom and dependency audit, which also writes the route of every numbered result for `route_check.py`; copy it to `scripts/Audit.lean` and fill in its lists |
| `assets/lean_action_ci.yml` | CI: build, the audit's imports, audit, route check, the Challenge's copy of shared definitions, links, tables |
| `assets/palomar_preflight.yml` | Palomar's mechanical preflight, run on demand |
