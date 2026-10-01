#!/usr/bin/env python3
"""Convert Lean files to the module system.

usage: to_module.py FILE.lean...

For each file that does not yet start with `module`: put `module` first, turn every `import`
into `public import`, and open `@[expose] public section` after the imports. Files that already
use the module system are left alone. Afterwards, rebuild and fix what breaks: private
declarations used in public statements, and module docstrings placed before `module`.
"""
import pathlib
import sys

for path in sys.argv[1:]:
    p = pathlib.Path(path)
    lines = p.read_text(encoding='utf-8').split('\n')
    if any(l.strip() == 'module' for l in lines[:20]):
        continue
    last_import = max((i for i, l in enumerate(lines) if l.startswith('import ')), default=-1)
    out = ['module', '']
    for l in lines[:last_import + 1]:
        if l.startswith('import '):
            out.append('public ' + l)
        elif l.strip():
            out.append(l)
    rest = lines[last_import + 1:]
    while rest and not rest[0].strip():
        rest = rest[1:]
    out += ['', '@[expose] public section', ''] + rest
    p.write_text('\n'.join(out), encoding='utf-8')
    print('converted', path)
