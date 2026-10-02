#!/usr/bin/env python3
"""Replace the proofs of declarations that contain errors by `sorry`.

usage: autosorry.py FILE.lean ERRORS.txt

ERRORS.txt holds Lean output; lines `FILE:LINE:COL: error: ...` are used.
Errors inside a theorem/lemma/example/instance body (after its top-level `:=`)
cause the body to be replaced by `by sorry`. Other errors are printed as
"manual" so they can be fixed by hand. Prints a summary.
"""
import re
import sys

DECL = re.compile(
    r'^(?:@\[[^\]]*\]\s*)*(?:(?:private|protected|noncomputable|nonrec|partial|unsafe|public|meta)\s+)*'
    r'(theorem|lemma|def|abbrev|instance|example|opaque|structure|class|inductive)\b')
BOUNDARY = re.compile(
    r'^(end\b|section\b|namespace\b|open\b|variable\b|set_option\b|/-!|/--|@\[|#|noncomputable section'
    r'|omit\b|include\b|attribute\b|local\b|scoped\b|universe\b|alias\b|export\b|private\b|protected\b'
    r'|theorem\b|lemma\b|def\b|abbrev\b|instance\b|example\b|opaque\b|structure\b|class\b|inductive\b'
    r'|noncomputable\b|public\b|meta\b|macro\b|syntax\b|notation\b|infix|prefix|postfix|elab\b|deriving\b'
    r'|mutual\b|/-)')

SORRYABLE = {'theorem', 'lemma', 'example', 'instance'}


def strip_comments_and_strings(text):
    """Return text with comments and strings replaced by spaces (same length)."""
    out = list(text)
    i, n = 0, len(text)
    depth = 0
    while i < n:
        if text.startswith('/-', i):
            depth = 1
            j = i + 2
            while j < n and depth > 0:
                if text.startswith('/-', j):
                    depth += 1
                    j += 2
                elif text.startswith('-/', j):
                    depth -= 1
                    j += 2
                else:
                    j += 1
            for k in range(i, j):
                if out[k] != '\n':
                    out[k] = ' '
            i = j
        elif text.startswith('--', i):
            j = text.find('\n', i)
            if j == -1:
                j = n
            for k in range(i, j):
                out[k] = ' '
            i = j
        elif text[i] == '"':
            j = i + 1
            while j < n and text[j] != '"':
                if text[j] == '\\':
                    j += 1
                j += 1
            for k in range(i, min(j + 1, n)):
                if out[k] != '\n':
                    out[k] = ' '
            i = j + 1
        else:
            i += 1
    return ''.join(out)


def main():
    path, errpath = sys.argv[1], sys.argv[2]
    src = open(path, encoding='utf-8').read()
    lines = src.split('\n')
    clean = strip_comments_and_strings(src).split('\n')
    errors = []
    base = path.split('/')[-1]
    for l in open(errpath, encoding='utf-8'):
        m = re.match(r"^(?:error: )?(\S+?):(\d+):(\d+):(?: error)?", l) if ("error" in l[:200]) else None
        if m and m.group(1).endswith(base):
            errors.append((int(m.group(2)), int(m.group(3)), l.strip()))
    # Find declarations: (start_line_idx, kind, end_line_idx_exclusive)
    decls = []
    i = 0
    n = len(lines)
    while i < n:
        m = DECL.match(clean[i])
        if m:
            kind = m.group(1)
            j = i + 1
            while j < n:
                c = clean[j]
                if c and not c[0].isspace() and BOUNDARY.match(c) and not c.startswith('|'):
                    break
                j += 1
            # trim trailing blank lines
            k = j
            while k > i + 1 and not clean[k - 1].strip():
                k -= 1
            decls.append([i, kind, k])
            i = j
        else:
            i += 1
    # For each decl, find top-level ':=' position
    for d in decls:
        s, kind, e = d
        depth = 0
        pos = None
        for li in range(s, e):
            c = clean[li]
            col = 0
            while col < len(c):
                ch = c[col]
                if ch in '([{⟨⦃':
                    depth += 1
                elif ch in ')]}⟩⦄':
                    depth -= 1
                elif c.startswith(':=', col) and depth == 0 and not re.match(r'^\s*(letI|haveI|let|have)\b', c[:col]):
                    pos = (li, col)
                    break
                col += 1
            if pos:
                break
        d.append(pos)
    to_sorry = set()
    manual = []
    for (ln, col, msg) in errors:
        li = ln - 1
        owner = None
        for idx, d in enumerate(decls):
            if d[0] <= li < max(d[2], d[0] + 1):
                owner = idx
                break
        if owner is None:
            manual.append((ln, col, msg, 'outside decl'))
            continue
        s, kind, e, pos = decls[owner]
        if pos is None or kind not in SORRYABLE:
            manual.append((ln, col, msg, f'{kind} without body or not sorryable'))
            continue
        pl, pc = pos
        if li > pl or (li == pl and col - 1 >= pc):
            to_sorry.add(owner)
        else:
            manual.append((ln, col, msg, 'statement'))
    # Apply replacements bottom-up
    names = []
    for idx in sorted(to_sorry, reverse=True):
        s, kind, e, pos = decls[idx]
        pl, pc = pos
        header = lines[pl][:pc]
        name_m = re.search(r'(?:theorem|lemma|instance|example)\s+([^\s:({\[]*)', clean[s])
        names.append((s + 1, name_m.group(1) if name_m else '?'))
        new = [header.rstrip() + ' := by', '  sorry']
        # preserve indentation style: if header is only whitespace, keep ':= by' on that line
        if not header.strip():
            new = [header + ':= by', '  sorry']
        lines[pl:e] = new
    open(path, 'w', encoding='utf-8').write('\n'.join(lines))
    for ln, name in sorted(names):
        print(f'SORRIED {path}:{ln} {name}')
    for ln, col, msg, why in manual:
        print(f'MANUAL [{why}] {msg}')


if __name__ == '__main__':
    main()
