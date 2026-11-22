#!/usr/bin/env python3
"""Copy the shared definitions of a library module into the Challenge, or check the copy.

Comparator requires every constant that a Challenge statement uses to be the same in the
Challenge and in the Solution's environment. When the statements need definitions too large to
restate inline, keep them in one module of the library, `PaperName/Defs.lean`, between the two
marker lines below, and let this script copy that block verbatim into the Challenge,
`palomar/PaperName/Challenge.lean`, which may not import the project.
The Solution imports the library, so both environments then contain the same definitions.

Run from the repository root:

    python3 scripts/sync_challenge_defs.py           # rewrite the block in the Challenge
    python3 scripts/sync_challenge_defs.py --check   # exit 1 if the copy differs (for CI)

Configure the block below for the project. A repository with several papers lists one
`(definitions module, Challenge)` pair per paper in `PAIRS` (references/multi-paper.md); every
pair is copied, or checked, in turn.
"""

import sys
from pathlib import Path

# ---- configuration -------------------------------------------------------------------------
# The library module that holds the shared definitions, and the Challenge file.
DEFS = 'PaperName/Defs.lean'
CHALLENGE = 'palomar/PaperName/Challenge.lean'
# With several papers, one (definitions module, Challenge) pair per paper, e.g.
#   PAIRS = [('ProjectName/PaperA/Defs.lean', 'palomar/PaperA/Challenge.lean'),
#            ('ProjectName/PaperB/Defs.lean', 'palomar/PaperB/Challenge.lean')]
# When PAIRS is empty, the single pair (DEFS, CHALLENGE) is used.
PAIRS = []
# The marker lines around the shared block, in both files.
BEGIN = '-- BEGIN SHARED DEFINITIONS\n'
END = '-- END SHARED DEFINITIONS\n'
# ---------------------------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent


def block(text: str, name: str) -> tuple[int, int]:
    """The span of the shared block in `text`, markers included."""
    i, j = text.find(BEGIN), text.find(END)
    if i < 0 or j < i or text.count(BEGIN) != 1 or text.count(END) != 1:
        sys.exit(f'{name}: expected exactly one pair of markers')
    return i, j + len(END)


def sync(defs_name: str, chal_name: str, check: bool) -> bool:
    """Copy (or, with `check`, compare) the shared block of one pair; return whether it was current."""
    defs_path, chal_path = ROOT / defs_name, ROOT / chal_name
    defs, chal = defs_path.read_text(), chal_path.read_text()
    di, dj = block(defs, defs_name)
    ci, cj = block(chal, chal_name)
    shared = defs[di:dj]
    if check:
        if chal[ci:cj] != shared:
            print(f'{chal_name}: the shared definitions differ from {defs_name}; '
                  f'run python3 scripts/sync_challenge_defs.py')
            return False
        print(f'{chal_name}: the shared definitions match {defs_name}')
        return True
    chal_path.write_text(chal[:ci] + shared + chal[cj:])
    print(f'{chal_name}: shared definitions copied from {defs_name}')
    return True


def main() -> None:
    args = sys.argv[1:]
    if args and args[0] in ('-h', '--help') or any(a != '--check' for a in args):
        print(__doc__.strip())
        sys.exit(0 if args and args[0] in ('-h', '--help') else 2)
    check = '--check' in args
    pairs = PAIRS or [(DEFS, CHALLENGE)]
    current = [sync(d, c, check) for d, c in pairs]
    if not all(current):
        sys.exit(1)


if __name__ == '__main__':
    main()
