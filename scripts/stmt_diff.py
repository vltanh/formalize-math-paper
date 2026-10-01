#!/usr/bin/env python3
"""List the declarations whose statements or definitions changed since a git revision.

usage: stmt_diff.py REV [PATH...] [--defs-only | --statements-only]

Compares every declaration in the tracked .lean files under PATH (default: all tracked .lean
files) at REV with the working tree:

- theorems and lemmas: the statement, up to the top-level `:=`;
- definitions, abbreviations, structures, instances: the whole declaration.

Whitespace is ignored. Prints CHANGED (old and new, abbreviated), REMOVED, and the number of
declarations ADDED per file. Use it after parallel repair or cleanup, to catch statement changes
that nobody reported. A paper result must never appear here unless the change was intended and
documented.
"""
import argparse
import re
import subprocess
from pathlib import Path

DECL = re.compile(
    r"^(?:@\[[^\]]*\]\s*)*((?:private |protected |noncomputable |nonrec |public |meta )*)"
    r"(theorem|lemma|def|abbrev|instance|structure|inductive|class|opaque)\s+([^\s(\[{:]+)", re.M)
# Lines that end the previous declaration's text.
STOP = re.compile(
    r"^(?:/--|/-!|end\b|namespace\b|section\b|open\b|variable\b|omit\b|include\b|"
    r"noncomputable section|set_option\b|attribute\b|@\[|#)", re.M)


def top_level_assign(text):
    """Index of the first `:=` outside brackets, or len(text)."""
    depth = 0
    for i, ch in enumerate(text):
        if ch in '([{⟨⦃':
            depth += 1
        elif ch in ')]}⟩⦄':
            depth -= 1
        elif text.startswith(':=', i) and depth == 0:
            return i
    return len(text)


def declarations(text):
    out = {}
    ms = list(DECL.finditer(text))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        body = text[m.start():end]
        stop = STOP.search(body, 1)
        if stop:
            body = body[:stop.start()]
        kind = m.group(2)
        if kind in ('theorem', 'lemma'):
            body = body[:top_level_assign(body)]
        out[m.group(3)] = (kind, ' '.join(body.split()))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('rev')
    ap.add_argument('paths', nargs='*')
    group = ap.add_mutually_exclusive_group()
    group.add_argument('--defs-only', action='store_true')
    group.add_argument('--statements-only', action='store_true')
    args = ap.parse_args()
    files = subprocess.run(['git', 'ls-files', '--', *(args.paths or ['*.lean'])],
                           capture_output=True, text=True, check=True).stdout.split()
    files = [f for f in files if f.endswith('.lean')]
    # A file that did not exist at REV (for example, a renamed one) is reported as NEW FILE.
    for f in files:
        old = subprocess.run(['git', 'show', f'{args.rev}:{f}'], capture_output=True, text=True).stdout
        new = Path(f).read_text(encoding='utf-8')
        a, b = declarations(old), declarations(new)
        for name, (kind, stmt) in a.items():
            is_thm = kind in ('theorem', 'lemma')
            if (args.defs_only and is_thm) or (args.statements_only and not is_thm):
                continue
            if name not in b:
                if old:
                    print(f'REMOVED {f}: {name}')
            elif b[name][1] != stmt:
                print(f'CHANGED {f}: {name}\n   OLD: {stmt[:500]}\n   NEW: {b[name][1][:500]}')
        added = [n for n in b if n not in a]
        if added and old:
            print(f'ADDED {f}: {len(added)}')
        elif not old:
            print(f'NEW FILE {f}: {len(b)} declarations')


if __name__ == '__main__':
    main()
