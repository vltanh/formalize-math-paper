#!/usr/bin/env python3
"""List the declarations whose statements or definitions changed since a git revision.

usage: stmt_diff.py REV [PATH...] [--defs-only | --statements-only]

Compares every declaration in the tracked .lean files under PATH (default: all tracked .lean
files) at REV with the working tree:

- theorems and lemmas: the statement, up to the top-level `:=`;
- definitions, abbreviations, structures, instances: the whole declaration.

Declarations are identified by their full names (`namespace` blocks included), and a change to a
file's `variable` commands, which changes the statements that use them, is reported too. A file
that git sees as renamed since REV (moved with `git mv`, as when a second paper joins a project and
the first paper's code moves) is compared with its old path. A file deleted since REV is reported
as DELETED FILE, and each of its declarations is looked for in the current files: found, it is
MOVED (and CHANGED if its statement differs); not found, REMOVED. Whitespace is ignored. Prints
RENAMED, CHANGED (old and new, abbreviated), REMOVED, MOVED, DELETED FILE, VARIABLES, and the
number of declarations ADDED per file. Use it after parallel repair, cleanup or a move, to catch statement changes that nobody
reported. A paper result must never appear here unless the change was intended and documented.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from strip_call_args import mask, scopes  # noqa: E402

DECL = re.compile(
    r"^[ \t]*(?:@\[[^\]]*\]\s*)*((?:private |protected |noncomputable |nonrec |public |meta )*)"
    r"(theorem|lemma|def|abbrev|instance|structure|inductive|class|opaque)\s+([^\s(\[{:]+?)\.?(?=[\s(\[{:⦃]|\.\{)",
    re.M)
VARIABLE = re.compile(r"^variable\b.*(?:\n[ \t]+\S.*)*", re.M)
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
    """{full name: (kind, normalized statement or definition)}, and the `variable` commands."""
    out = {}
    masked = mask(text)
    info = scopes(masked)
    ms = list(DECL.finditer(masked))
    for i, m in enumerate(ms):
        end = ms[i + 1].start() if i + 1 < len(ms) else len(text)
        body = text[m.start():end]
        stop = STOP.search(body, 1)
        if stop:
            body = body[:stop.start()]
        kind = m.group(2)
        if kind in ('theorem', 'lemma'):
            body = body[:top_level_assign(body)]
        name = m.group(3)
        prefix = info[text.count('\n', 0, m.start(3))][0][0]
        full = name[len('_root_.'):] if name.startswith('_root_.') else '.'.join(
            p for p in (prefix, name) if p)
        out[full] = (kind, ' '.join(body.split()))
    variables = [' '.join(v.split()) for v in VARIABLE.findall(mask(text))]
    return out, variables


def renamed_from(rev):
    """{path now: path at REV} for the .lean files that git sees as renamed since REV."""
    out = subprocess.run(['git', 'diff', '-M', '--name-status', '-z', rev, '--', '*.lean'],
                         capture_output=True, text=True).stdout.split('\0')
    renames, i = {}, 0
    while i + 1 < len(out):
        if out[i].startswith('R') and i + 2 < len(out):
            renames[out[i + 2]] = out[i + 1]
            i += 3
        else:
            i += 2
    return renames


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('rev')
    ap.add_argument('paths', nargs='*')
    group = ap.add_mutually_exclusive_group()
    group.add_argument('--defs-only', action='store_true')
    group.add_argument('--statements-only', action='store_true')
    args = ap.parse_args()
    if subprocess.run(['git', 'rev-parse', '--verify', '--quiet', f'{args.rev}^{{commit}}'],
                      capture_output=True).returncode:
        sys.exit(f'not a commit: {args.rev}')
    files = subprocess.run(['git', 'ls-files', '-z', '--', *(args.paths or ['*.lean'])],
                           capture_output=True, text=True, check=True).stdout.split('\0')
    files = [f for f in files if f.endswith('.lean') and Path(f).is_file()]
    renames = renamed_from(args.rev)
    current = {}  # name -> [(file, kind, statement)] over the current files
    # A file that did not exist at REV, and is not a renamed one, is reported as NEW FILE.
    for f in files:
        src = renames.get(f, f)
        old = subprocess.run(['git', 'show', f'{args.rev}:./{src}'], capture_output=True,
                             text=True).stdout
        if src != f:
            print(f'RENAMED {src} -> {f}')
        new = Path(f).read_text(encoding='utf-8')
        (a, va), (b, vb) = declarations(old), declarations(new)
        for name, (kind, stmt) in b.items():
            current.setdefault(name, []).append((f, kind, stmt))
        if old and va != vb:
            print(f'VARIABLES {f}:\n   OLD: {va}\n   NEW: {vb}')
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
    # Files deleted since REV, a rename that git does not detect included: their declarations may
    # have moved to another file, or gone.
    deleted = subprocess.run(['git', 'diff', '-M', '--diff-filter=D', '--name-only', '-z', args.rev,
                              '--', *(args.paths or ['*.lean'])],
                             capture_output=True, text=True, check=True).stdout.split('\0')
    for f in (d for d in deleted if d.endswith('.lean')):
        old = subprocess.run(['git', 'show', f'{args.rev}:./{f}'], capture_output=True,
                             text=True).stdout
        a, _ = declarations(old)
        print(f'DELETED FILE {f}: {len(a)} declarations')
        for name, (kind, stmt) in a.items():
            is_thm = kind in ('theorem', 'lemma')
            if (args.defs_only and is_thm) or (args.statements_only and not is_thm):
                continue
            homes = current.get(name, [])
            if not homes:
                print(f'REMOVED {f}: {name}')
                continue
            print(f'MOVED {name}: {f} -> {", ".join(h[0] for h in homes)}')
            for g, _, new_stmt in homes:
                if new_stmt != stmt:
                    print(f'CHANGED {g}: {name}\n   OLD: {stmt[:500]}\n   NEW: {new_stmt[:500]}')


if __name__ == '__main__':
    main()
