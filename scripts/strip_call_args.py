#!/usr/bin/env python3
"""Delete, at every call site, the arguments of binders that were removed from declarations.

usage: strip_call_args.py REV [--dry-run]

After strip_unused.py (or a manual cleanup) deletes explicit hypotheses from declarations, their
callers still pass the old arguments. This script compares the explicit binders `( … )` of every
theorem, lemma and definition in the working tree with the same declaration at the git revision
REV (the commit before the cleanup), and deletes the corresponding argument at each call site in
the tracked .lean files.

It handles arguments that are identifiers with projections (`hK.2.1`), parenthesized terms with
projections (`(foo a).1`), anonymous constructors (`⟨a, b⟩`) and numerals, and it skips named
arguments (`(h := …)`). Call sites that it cannot parse are listed for manual repair: an
argument on the next line, a partial application, or a declaration used as a function value.

Run it once, right after the binders are removed. A second run would see call sites that already
lack the arguments and report them all for manual repair. Rebuild afterwards: an implicit argument
that only the removed hypothesis determined may have to be given by name at some call sites, as in
`(K := K)` or `(t := t)`.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

OPEN, CLOSE = '({[⦃⟨', ')}]⦄⟩'
IDCH = re.compile(r"[\w.'!?₀-₉ₐ-ₜα-ωΑ-Ωℓ]")
DECL = re.compile(r"^(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|noncomputable|nonrec|public|meta)\s+)*"
                  r"(?:theorem|lemma|def|abbrev)\s+([^\s(\[{:]+)", re.M)
STOP_WORDS = {'with', 'at', 'using', 'from', 'then', 'else', 'do', 'by', 'fun', 'show', 'in', 'only'}


def explicit_binders(text, name):
    """The names bound by the explicit binders `( … )` of declaration `name`, in order."""
    m = re.search(r"^(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|noncomputable|nonrec|public|meta)\s+)*"
                  r"(?:theorem|lemma|def|abbrev)\s+" + re.escape(name) + r"(?=[\s(\[{:])", text, re.M)
    if not m:
        return None
    i, depth, start, names = m.end(), 0, None, []
    while i < len(text):
        ch = text[i]
        if depth == 0 and ch == ':':
            break
        if ch in OPEN:
            if depth == 0:
                start = (ch, i)
            depth += 1
        elif ch in CLOSE:
            depth -= 1
            if depth == 0 and start and start[0] == '(':
                names.extend(text[start[1] + 1:i].split(':')[0].split())
        i += 1
    return names


def parse_arg(s, i):
    """(start, end, named) of the argument at or after i on the same line, or None."""
    j = i
    while j < len(s) and s[j] in ' \t':
        j += 1
    if j >= len(s) or s[j] in ',)]⟩}|\n' or s.startswith(':=', j):
        return None
    if s[j] in '(⟨[':
        depth, k = 0, j
        while k < len(s):
            if s[k] in OPEN:
                depth += 1
            elif s[k] in CLOSE:
                depth -= 1
                if depth == 0:
                    break
            k += 1
        k += 1
        while k + 1 < len(s) and s[k] == '.' and IDCH.match(s[k + 1]):
            k += 1
            while k < len(s) and IDCH.match(s[k]):
                k += 1
        named = s[j] == '(' and re.match(r"\(\s*[\w'₀-₉]+\s*:=", s[j:k]) is not None
        return j, k, named
    if IDCH.match(s[j]):
        k = j
        while k < len(s) and IDCH.match(s[k]):
            k += 1
        if s[j:k] in STOP_WORDS:
            return None
        return j, k, False
    return None


def strip_calls(name, removed, files, dry_run):
    pat = re.compile(r"(?<![\w.'`])(?:[A-Z][\w']*\.)*" + re.escape(name) + r"(?![\w'])")
    fixed, manual = 0, []
    for f in files:
        s = f.read_text(encoding='utf-8')
        out, pos, changed = [], 0, False
        for m in pat.finditer(s):
            line_start = s.rfind('\n', 0, m.start()) + 1
            if DECL.match(s, line_start) and DECL.match(s, line_start).group(1).split('.')[-1] == name:
                continue
            if m.start() < pos:
                continue
            i, args = m.end(), []
            while len(args) <= max(removed):
                a = parse_arg(s, i)
                if a is None:
                    break
                i = a[1]
                if not a[2]:
                    args.append(a)
            if len(args) <= max(removed):
                line = s.count('\n', 0, m.start()) + 1
                manual.append(f'{f}:{line}: {s[m.start():m.start() + 70]!r}')
                continue
            segs, last = [], pos
            for idx in sorted(removed):
                a0, a1, _ = args[idx]
                ws = a0
                while ws > 0 and s[ws - 1] in ' \t':
                    ws -= 1
                segs.append(s[last:ws])
                last = a1
            out.append(''.join(segs))
            pos, changed = last, True
            fixed += 1
        if changed and not dry_run:
            out.append(s[pos:])
            f.write_text(''.join(out), encoding='utf-8')
    return fixed, manual


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('rev')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    paths = subprocess.run(['git', 'ls-files', '*.lean'], capture_output=True, text=True,
                           check=True).stdout.split()
    files = [Path(p) for p in paths]
    changes = []
    for f in files:
        old = subprocess.run(['git', 'show', f'{args.rev}:{f}'], capture_output=True, text=True)
        if old.returncode != 0:
            continue
        new_text = f.read_text(encoding='utf-8')
        for m in DECL.finditer(new_text):
            name = m.group(1).split('.')[-1]
            new_b = explicit_binders(new_text, m.group(1))
            old_b = explicit_binders(old.stdout, m.group(1))
            if new_b is None or old_b is None or len(old_b) <= len(new_b):
                continue
            removed = [k for k, b in enumerate(old_b) if b not in new_b]
            if removed and [b for b in old_b if b in new_b] == new_b:
                changes.append((name, removed, old_b))
    if not changes:
        print('no declaration lost an explicit binder since', args.rev)
        return 0
    status = 0
    for name, removed, old_b in changes:
        fixed, manual = strip_calls(name, removed, files, args.dry_run)
        dropped = ', '.join(old_b[k] for k in removed)
        print(f'{name}: drop argument(s) {dropped} at {fixed} call site(s)')
        for line in manual:
            print('  MANUAL', line)
            status = 1
    return status


if __name__ == '__main__':
    sys.exit(main())
