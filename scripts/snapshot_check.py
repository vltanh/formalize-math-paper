#!/usr/bin/env python3
"""Check Lean files against a private snapshot of the project's compiled modules.

usage: snapshot_check.py take SNAPDIR [--force]
       snapshot_check.py check SNAPDIR FILE.lean [--emit]

Run from the project root. When several agents work in one checkout, a `lake build` started by one
of them rebuilds, and meanwhile deletes, the `.olean` files that the others import ("object file …
does not exist"), and a module rebuilt from a half-edited file breaks everyone downstream. Each
agent can work against its own copy of the build outputs instead:

- `take` copies `.lake/build/lib/lean` to SNAPDIR, which must be new, empty, or an earlier
  snapshot. It refuses when `lake build --no-build` says the build is out of date, because the copy
  would mix versions; rebuild first, or pass --force.
- `check` runs `lean` on FILE with the lakefile's `[leanOptions]`. The snapshot replaces the
  project's own build directory; Mathlib and the other packages come from `.lake/packages`.
- `--emit` also writes the file's `.olean` and `.ilean` into the snapshot, so that the agent's
  later files can import its new version.

Nothing in the project's `.lake` changes. Take a fresh snapshot when upstream modules that the
agent uses have changed their statements.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_file import lean_options  # noqa: E402

BUILD = Path('.lake/build/lib/lean')
MARKER = '.snapshot_check'


def lean_path(snap):
    out = subprocess.run(['lake', 'env', 'printenv', 'LEAN_PATH'], capture_output=True, text=True,
                         check=True).stdout.strip()
    own = BUILD.resolve()
    entries = [str(snap) if Path(e).resolve() == own else e for e in out.split(os.pathsep) if e]
    if str(snap) not in entries:
        entries.insert(0, str(snap))
    return os.pathsep.join(entries)


def take(snap, force):
    if not BUILD.is_dir():
        sys.exit('no .lake/build/lib/lean: run `lake build` first')
    here = Path.cwd().resolve()
    if snap == here or snap in here.parents or (here / '.lake') in [snap, *snap.parents]:
        sys.exit(f'refusing to use {snap} as a snapshot directory')
    if snap.exists() and any(snap.iterdir()) and not (snap / MARKER).is_file():
        sys.exit(f'{snap} exists and is not a snapshot: choose a new directory')
    fresh = subprocess.run(['lake', 'build', '--no-build'], capture_output=True, text=True)
    if fresh.returncode != 0 and not force:
        sys.exit('the build is not up to date (rebuild first, or --force):\n' +
                 '\n'.join((fresh.stdout + fresh.stderr).splitlines()[-20:]))
    if snap.exists():
        shutil.rmtree(snap)
    shutil.copytree(BUILD, snap, symlinks=True)
    (snap / MARKER).write_text('snapshot of .lake/build/lib/lean, made by snapshot_check.py\n')
    print(f'snapshot of {sum(1 for _ in snap.rglob("*.olean"))} modules in {snap}')


def check(snap, file, emit):
    if not snap.is_dir():
        sys.exit(f'no snapshot at {snap}: run "snapshot_check.py take {snap}" first')
    env = dict(os.environ, LEAN_PATH=lean_path(snap))
    cmd = ['lean', *lean_options(), '-R', '.']
    if emit:
        try:
            rel = Path(file).resolve().relative_to(Path.cwd().resolve())
        except ValueError:
            sys.exit(f'--emit needs a file inside the project: {file}')
        stem = snap / rel.with_suffix('')
        stem.parent.mkdir(parents=True, exist_ok=True)
        cmd += ['-o', f'{stem}.olean', '-i', f'{stem}.ilean']
    result = subprocess.run(cmd + [file], env=env, capture_output=True, text=True)
    sys.stdout.write(result.stdout + result.stderr)
    return result.returncode


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    t = sub.add_parser('take')
    t.add_argument('snapdir')
    t.add_argument('--force', action='store_true')
    c = sub.add_parser('check')
    c.add_argument('snapdir')
    c.add_argument('file')
    c.add_argument('--emit', action='store_true')
    args = ap.parse_args()
    if not (Path('lakefile.toml').is_file() or Path('lakefile.lean').is_file()):
        sys.exit('run from the project root, the directory of the lakefile')
    snap = Path(args.snapdir).resolve()
    if args.cmd == 'take':
        take(snap, args.force)
        return 0
    return check(snap, args.file, args.emit)


if __name__ == '__main__':
    sys.exit(main())
