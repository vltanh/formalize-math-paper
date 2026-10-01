#!/usr/bin/env python3
"""Delete the binders that Lean's unused-variables linter reports.

usage: strip_unused.py BUILD_LOG [--dry-run]

BUILD_LOG is the output of `lake build` (or `lake env lean`), with warnings such as
  warning: Pkg/File.lean:12:5: Variable name `hx` is not explicitly referenced.

For each such variable bound in a declaration's signature, its binder is removed: `(hx : P)`
disappears, and in a group such as `(a b : T)` only the name goes. Variables that are not in a
signature (for example `fun x =>` or `∃ x,` in a body, or a pattern variable) are listed for manual
repair and left alone.

After running it: rebuild; the errors point at call sites that still pass the removed arguments;
delete those arguments; repeat while new warnings appear, because a removal can leave the caller's
hypotheses unused in turn.
"""
import argparse
import re
from collections import defaultdict
from pathlib import Path

WARN = re.compile(r"warning: ([^:\s]+\.lean):(\d+):(\d+): Variable name `([^`]+)` is not explicitly referenced")
DECL = re.compile(r"^(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|noncomputable|nonrec|public|meta)\s+)*"
                  r"(theorem|lemma|def|abbrev|instance|structure|example|opaque)\b")
OPEN, CLOSE = '({[⦃⟨', ')}]⦄⟩'


def signature_end(text, start):
    """Offset of the declaration's top-level `:=` (or `where`/`|`), starting at `start`."""
    depth = 0
    i = start
    while i < len(text):
        ch = text[i]
        if ch in OPEN:
            depth += 1
        elif ch in CLOSE:
            depth -= 1
        elif depth == 0 and (text.startswith(':=', i) or text.startswith(' where', i)
                             or (ch == '|' and text[i - 1] == '\n')):
            return i
        i += 1
    return len(text)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('log')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()
    warnings = sorted(set(WARN.findall(Path(args.log).read_text(encoding='utf-8'))))
    by_file = defaultdict(list)
    for f, l, c, var in warnings:
        by_file[f].append((int(l), int(c), var))
    manual, total = [], 0
    for f, items in by_file.items():
        text = Path(f).read_text(encoding='utf-8')
        lines = text.split('\n')
        starts = [0]
        for ln in lines:
            starts.append(starts[-1] + len(ln) + 1)
        groups = {}
        for l, c, var in items:
            pos = starts[l - 1] + c
            if text[pos:pos + len(var)] != var:
                manual.append(f'{f}:{l}:{c} `{var}`: source changed since the build; rebuild first')
                continue
            # The declaration containing the variable, and the end of its signature.
            decl_line = next((i for i in range(l - 1, -1, -1) if DECL.match(lines[i])), None)
            if decl_line is None or pos >= signature_end(text, starts[decl_line]):
                manual.append(f'{f}:{l}:{c} `{var}`: not in a signature; rename it `_` or restate')
                continue
            # The innermost bracket group around the variable.
            depth, i = 0, pos - 1
            while i >= starts[decl_line]:
                if text[i] in CLOSE:
                    depth += 1
                elif text[i] in OPEN:
                    if depth == 0:
                        break
                    depth -= 1
                i -= 1
            if i < starts[decl_line]:
                manual.append(f'{f}:{l}:{c} `{var}`: no enclosing binder found')
                continue
            depth, j = 0, i + 1
            while True:
                if text[j] in OPEN:
                    depth += 1
                elif text[j] in CLOSE:
                    if depth == 0:
                        break
                    depth -= 1
                j += 1
            group = text[i:j + 1]
            inner = group[1:-1]
            if ':' not in inner or var not in inner[:inner.index(':')].split():
                manual.append(f'{f}:{l}:{c} `{var}`: inside {group[:60]!r}, not a binder name')
                continue
            groups.setdefault((i, j + 1), [group, set()])[1].add(var)
        edits = []
        for (o, e), (group, names) in groups.items():
            inner = group[1:-1]
            colon = inner.index(':')
            rest = [n for n in inner[:colon].split() if n not in names]
            if rest:
                edits.append((o, e, group[0] + ' '.join(rest) + ' :' + inner[colon + 1:] + group[-1]))
            else:
                a, b = o, e
                if b < len(text) and text[b] == ' ':
                    b += 1
                elif a > 0 and text[a - 1] == ' ':
                    a -= 1
                ls, le = text.rfind('\n', 0, a) + 1, text.find('\n', b)
                if text[ls:a].strip() == '' and text[b:le].strip() == '':
                    a, b = ls, le + 1
                edits.append((a, b, ''))
            total += 1
            print(f'{f}: remove {sorted(names)} from {" ".join(group.split())[:80]}')
        if not args.dry_run:
            for a, b, new in sorted(edits, reverse=True):
                text = text[:a] + new + text[b:]
            Path(f).write_text(text, encoding='utf-8')
    print(f'{total} binder groups {"would be " if args.dry_run else ""}edited')
    if manual:
        print('manual:')
        print('\n'.join('  ' + m for m in manual))


if __name__ == '__main__':
    main()
