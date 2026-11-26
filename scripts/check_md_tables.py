#!/usr/bin/env python3
"""Check that every row of every Markdown table has as many cells as its header.

usage: check_md_tables.py FILE.md... [--fix]

In GitHub-flavored Markdown, every unescaped `|` in a table row ends a cell, even inside a code
span. So `` `|S| ≥ 2` `` in a table cell breaks the row into extra cells. The script reports such
rows. With --fix, it escapes the pipes inside code spans of table rows (`\\|`, which renders as
`|`) and checks again. Lines inside fenced code blocks are not tables, and are left alone. Exits
with status 1 if a broken row remains.
"""
import argparse
import re
import sys
from pathlib import Path

RULE = re.compile(r'^\|\s*:?-{3}')
PIPE = re.compile(r'(?<!\\)\|')
FENCE = re.compile(r'^\s*(`{3,}|~{3,})')


def fenced(lines):
    """For each line, whether it is inside a fenced code block (fences included)."""
    out, fence = [], None
    for line in lines:
        m = FENCE.match(line)
        if fence:
            out.append(True)
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
        elif m:
            out.append(True)
            fence = m.group(1)
        else:
            out.append(False)
    return out


def table_rows(lines):
    """The indices of the rows of every table outside fenced code blocks: a header, its rule and
    the rows that follow."""
    code, rows, i = fenced(lines), [], 0
    while i < len(lines):
        if (not code[i] and lines[i].startswith('|') and i + 1 < len(lines)
                and RULE.match(lines[i + 1])):
            j = i + 2
            while j < len(lines) and not code[j] and lines[j].startswith('|'):
                j += 1
            rows.append(range(i, j))
            i = j
        else:
            i += 1
    return rows


def escape_code_spans(line):
    return re.sub(r'`[^`\n]*`', lambda m: m.group(0).replace('\\|', '|').replace('|', '\\|'), line)


def broken_rows(lines):
    out = []
    for table in table_rows(lines):
        cells = len(PIPE.findall(lines[table[0]]))
        out += [j for j in table[2:] if len(PIPE.findall(lines[j])) != cells]
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('files', nargs='+')
    ap.add_argument('--fix', action='store_true')
    args = ap.parse_args()
    bad = 0
    for f in args.files:
        lines = Path(f).read_text(encoding='utf-8').split('\n')
        if args.fix:
            rows = {j for table in table_rows(lines) for j in table}
            fixed = [escape_code_spans(l) if j in rows else l for j, l in enumerate(lines)]
            if fixed != lines:
                Path(f).write_text('\n'.join(fixed), encoding='utf-8')
                print(f'{f}: escaped pipes in code spans')
                lines = fixed
        for j in broken_rows(lines):
            bad += 1
            print(f'{f}:{j + 1}: cell count differs from the header: {lines[j][:100]}')
    print(f'{bad} broken table rows')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
