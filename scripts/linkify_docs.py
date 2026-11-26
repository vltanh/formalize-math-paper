#!/usr/bin/env python3
"""Link the Lean names in the Markdown documentation to the code.

Every inline code span that names a declaration, a module, a file or a directory of this
repository becomes a relative link; the link of a declaration points at the line of its
name. A declaration or module of a library that the project requires (`LIBRARIES`) links to its
line on GitHub, at the commit that `lake-manifest.json` pins. A code span that names a module of
the pinned Mathlib links to the module's page in Mathlib's documentation. Existing links are kept,
except links to a line of a Lean file, links into a library of `LIBRARIES` and links to the page of
a Mathlib module, which are recomputed: running the script after editing the code, or after moving
a pin, brings them up to date. Private files (the paths in `PRIVATE`, and anything git ignores)
are never linked, and existing links to them are removed, since they are not published. Fenced
code blocks, headings and table headers are left alone, and the text of a link may run over
several lines of a paragraph.

Run from the repository root, after `lake build` (and, when `LIBRARIES` names libraries,
`lake build <Library> …`, which compiles every module of each; a plain `lake build` compiles only
the modules that the project imports):

    python3 scripts/linkify_docs.py           # update the links
    python3 scripts/linkify_docs.py --check   # list the files whose links are out of date

The declaration locations come from the `.ilean` files that `lake build` writes.

Configure the block below for the project: the documents to process, the namespaces in which the
documents name declarations without their prefix, the top-level module names of the project, the
module whose declarations win when a name is declared twice (the Challenge, whose theorems the
Solution restates), and the libraries whose names link to GitHub.
"""

import argparse
import json
import functools
import os
import re
import subprocess
import sys
from pathlib import Path

# ---- configuration -------------------------------------------------------------------------
# The Markdown documents to process.
DOCS = ['README.md', 'docs/PaperName/REPORT.md', 'docs/PaperName/CREDITS.md']
# Namespaces in which the documents name declarations without their prefix, most specific last:
# the paper's library, then its Challenge.
NAMESPACES = ['PaperName', 'PaperNameChallenge']
# With several papers in one repository (references/multi-paper.md): the namespaces of the documents
# in each top-level directory, tried before `NAMESPACES`, so that a short name in a paper's documents
# names that paper's declaration; the first namespace that declares a name wins, and the longest
# directory that contains the document is used. Example:
# {'docs/PaperA': ['PaperA', 'PaperAChallenge'], 'docs/PaperB': ['PaperB', 'PaperBChallenge']}.
NAMESPACES_BY_DIR = {}
# Top-level module names of the project: a code span naming such a module links to its file. With
# one paper, every module is under `PaperName`: the library's (`PaperName.Main`,
# `PaperName.Basic.…`) and the Challenge and the Solution (`PaperName.Challenge`,
# `PaperName.Solution`). With several papers, the project's root and every paper's name (the root
# of its Challenge and Solution): ('ProjectName', 'PaperA', 'PaperB').
MODULE_ROOTS = ('PaperName',)
# The module whose declarations win when a name is declared in several modules: the Challenge,
# whose theorems the Solution restates. With several papers, a tuple of modules, one per paper
# (each Challenge repeats its own paper's definitions): ('PaperA.Challenge', 'PaperB.Challenge').
# In a package with Palomar entries, the library's definitions first, then the Challenges; the
# first module of the tuple that declares a name wins.
PREFERRED_MODULE = 'PaperName.Challenge'
# The source directory of each module root whose `lean_lib` has a `srcDir` other than the
# repository root: the Challenges and Solutions are in `palomar/`. With several papers, one entry
# per paper: {'PaperA': 'palomar', 'PaperB': 'palomar'}. A root can have modules in both places
# (with one paper, `PaperName.Challenge` in `palomar/` and `PaperName.Main` at the root): a module
# is looked for in its root's source directory first, then at the repository root.
SOURCE_DIRS = {'PaperName': 'palomar'}
# Directories, besides the document's own and the repository root, against which the paths in the
# documents of a given directory are resolved: a code span `REPORT.md` in the README names
# `docs/PaperName/REPORT.md`, and `Challenge.lean` names `palomar/PaperName/Challenge.lean`. With
# several papers, give each paper's document directory its own Palomar directory, and the umbrella
# README none: {'': ['.github/workflows'], 'docs/PaperA': ['palomar/PaperA'], …}.
PATH_BASES = {'': ['.github/workflows', 'docs/PaperName', 'palomar/PaperName'],
              'docs/PaperName': ['palomar/PaperName']}
# Paths that are never linked, whether or not git ignores them: the working notes, which are not
# published. Any other path that git ignores is not linked either.
PRIVATE = ('notes',)
# The libraries beyond Mathlib that the project requires and whose names the documents link to:
# each package's name in `lake-manifest.json`, which is also the root of its modules, and the
# address of its files on GitHub, up to the commit. Their names link to their lines at the commit
# that the manifest pins, so build them in full first (`lake build <Library>`), in CI too. Example:
# {'Convexity': 'https://github.com/<owner>/lean4-convexity/blob/'}.
LIBRARIES = {}
# ---------------------------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent


def private(path):
    """Whether `path` (relative to the repository root) must not be linked: a path in `PRIVATE`,
    or a file that git ignores (build outputs). Such files are not published, so a link to them
    would be broken in the repository."""
    parts = Path(os.path.normpath(path)).parts
    if any(part in PRIVATE for part in parts):
        return True
    return subprocess.run(['git', 'check-ignore', '-q', path], cwd=ROOT).returncode == 0

BUILD = ROOT / '.lake' / 'build' / 'lib' / 'lean'
MATHLIB = ROOT / '.lake' / 'packages' / 'mathlib'
DOCS_URL = 'https://leanprover-community.github.io/mathlib4_docs/'

# Lean's standard axioms, and the core modules that declare them.
CORE = {'propext': 'Init.Core', 'Classical.choice': 'Init.Prelude', 'Quot.sound': 'Init.Prelude'}

# Lean's identifiers may also use Greek letters, letter-like symbols such as `ℝ`, mathematical
# script letters, and subscripts.
LETTER = 'A-Za-z_\u0391-\u03a9\u03b1-\u03c9\u1f00-\u1ffe\u2100-\u214f\U0001d49c-\U0001d59f'
IDENT = re.compile("^[%s][%s0-9'!?.\u2080-\u2089\u2090-\u209c\u1d62-\u1d6a\u2c7c]*$" % (LETTER, LETTER))
# A link's destination may be written in angle brackets, which lets it contain parentheses.
TOKEN = re.compile(r'\[`([^`\n]+)`\]\((<[^>\n]*>|[^)\s]+)\)'  # a link whose text is a code span
                   r'|\[[^\[\]]*\]\((?:<[^>\n]*>|[^)\s]*)\)'  # any other link, perhaps over lines
                   r'|`([^`\n]+)`')                          # a code span
LINE_LINK = re.compile(r'^[^:#]+\.lean#L\d+$')
TABLE_RULE = re.compile(r'^\|\s*:?-{3}')
FENCE = re.compile(r'^\s*(`{3,}|~{3,})')


def warn(message):
    print('warning: ' + message, file=sys.stderr)


def module_file(module):
    """The file of `module`, relative to the repository root: in the source directory of its root
    (`SOURCE_DIRS`) when the file is there, otherwise at the repository root. Both hold modules of
    one root when the root is a paper's name (`PaperName.Challenge` in `palomar/`,
    `PaperName.Basic.X` at the root)."""
    path = '/'.join(module.split('.')) + '.lean'
    base = SOURCE_DIRS.get(module.split('.')[0])
    if base and (ROOT / base / path).is_file():
        return base + '/' + path
    return path


def dir_namespaces(doc_dir):
    """The namespaces of `NAMESPACES_BY_DIR` for a document in `doc_dir`: those of the longest
    configured directory that contains it."""
    best = None
    for d in NAMESPACES_BY_DIR:
        if (doc_dir == d or doc_dir.startswith(d + '/')) and (best is None or len(d) > len(best)):
            best = d
    return NAMESPACES_BY_DIR[best] if best is not None else []


def mathlib_page(module):
    """The page of a Mathlib module in Mathlib's documentation, or None for another name."""
    return DOCS_URL + module.replace('.', '/') + '.html' if module.startswith('Mathlib.') else None


@functools.lru_cache(maxsize=None)
def library_sources():
    """Each library of `LIBRARIES` that the manifest pins to a Git commit: its checkout and the
    commit to link to. A library required by path, while it is developed, has no published commit:
    its names are not linked."""
    if not LIBRARIES:
        return {}
    manifest = json.loads((ROOT / 'lake-manifest.json').read_text(encoding='utf-8'))
    pins = {pkg['name']: pkg for pkg in manifest.get('packages', [])}
    sources = {}
    for library in LIBRARIES:
        pkg = pins.get(library)
        if pkg is None or pkg.get('type') != 'git':
            warn('lake-manifest.json pins no Git commit of %s; its names are not linked' % library)
            continue
        sources[library] = (ROOT / '.lake' / 'packages' / library, pkg['rev'])
    return sources


def library_file(checkout, module):
    """The file of a module of a library, relative to its checkout: at its root, or in `palomar/`
    for the modules of a Palomar submission."""
    path = '/'.join(module.split('.')) + '.lean'
    if not (checkout / path).is_file() and (checkout / 'palomar' / path).is_file():
        return 'palomar/' + path
    return path


def library_url(library, module, line=None):
    """The address of a module of a library on GitHub, at the pinned commit."""
    checkout, rev = library_sources()[library]
    url = LIBRARIES[library] + rev + '/' + library_file(checkout, module)
    return url if line is None else '%s#L%d' % (url, line)


def load_locations():
    """Each declaration's module and the line of its name, read from the `.ilean` files, and the
    address on GitHub of each declaration of a library of `LIBRARIES`."""
    locations, preferred, rank, urls = {}, {}, {}, {}
    for library, (checkout, _) in library_sources().items():
        for ilean in sorted((checkout / '.lake' / 'build' / 'lib' / 'lean').rglob('*.ilean')):
            data = json.loads(ilean.read_text(encoding='utf-8'))
            # A library's build may also hold the outputs of the packages that it requires; only
            # its own modules hold its declarations.
            if not (checkout / library_file(checkout, data['module'])).is_file():
                continue
            for name, ranges in data.get('decls', {}).items():
                locations[name] = (data['module'], ranges[4] + 1)
                urls[name] = library_url(library, data['module'], ranges[4] + 1)
    for ilean in sorted(BUILD.rglob('*.ilean')):
        data = json.loads(ilean.read_text(encoding='utf-8'))
        # A restored build cache keeps the outputs of deleted modules; skip them.
        if not (ROOT / module_file(data['module'])).is_file():
            continue
        # The preferred module's declarations win over restatements elsewhere.
        preferred_modules = ((PREFERRED_MODULE,) if isinstance(PREFERRED_MODULE, str)
                             else tuple(PREFERRED_MODULE))
        for name, ranges in data.get('decls', {}).items():
            urls.pop(name, None)  # the project's own declaration wins over a library's
            # `ranges` holds the declaration's range, then its name's; lines count from 0.
            location = (data['module'], ranges[4] + 1)
            if data['module'] not in preferred_modules:
                locations[name] = location
                continue
            # Among the preferred modules, the first one that declares the name wins.
            index = preferred_modules.index(data['module'])
            if index <= rank.get(name, index):
                preferred[name], rank[name] = location, index
    locations.update(preferred)
    if not locations:
        sys.exit('no .ilean files under %s; run `lake build` first' % BUILD)
    return locations, urls


class Linker:
    def __init__(self, locations, urls):
        self.locations = locations
        self.urls = urls

    def place(self, name):
        """The link target of the declaration `name`: its line in this repository, or its address
        in a library."""
        if name in self.urls:
            return self.urls[name]
        module, line = self.locations[name]
        return '%s#L%d' % (module_file(module), line)

    def declaration(self, name, doc_dir=''):
        candidates = [name]
        # Short names such as `U` or `h` are variables, not declarations.
        if len(name) >= 4:
            own = [ns + '.' + name for ns in dir_namespaces(doc_dir)]
            # The directory's namespaces in order: the first that declares the name wins (the
            # library's before the Challenge's, whose Solution restates its theorems).
            own_hits = [c for c in own if c in self.locations]
            if name not in self.locations and own_hits:
                return self.place(own_hits[0])
            candidates += [ns + '.' + name for ns in NAMESPACES]
        hits = [c for c in candidates if c in self.locations]
        if not hits:
            return None
        if hits[0] != name and len(hits) > 1:
            warn('`%s` is ambiguous: %s' % (name, ', '.join(hits)))
            return None
        return self.place(hits[0])

    def target(self, text, doc_dir):
        """The repository path or URL that `text` names, or None."""
        path = text.rstrip('/')
        if path and not path.startswith(('/', '.')) and ' ' not in path:
            # A document's own directory comes first: `REPORT.md` in `docs/PaperA/README.md` is
            # `docs/PaperA/REPORT.md`.
            for base in ([doc_dir] if doc_dir else []) + [''] + PATH_BASES.get(doc_dir, []):
                candidate = os.path.normpath(os.path.join(base, path))
                if (ROOT / candidate).exists() and not private(candidate):
                    return candidate
        if not IDENT.match(text):
            return None
        for library, (checkout, _) in library_sources().items():
            if (text.startswith(library + '.')
                    and (checkout / library_file(checkout, text)).is_file()):
                return library_url(library, text)
        if text.split('.')[0] in MODULE_ROOTS:
            if (ROOT / module_file(text)).is_file():
                return module_file(text)
        if text.startswith('Mathlib.'):
            # Only a module of the pinned Mathlib has a page; a proposed module has none.
            if (MATHLIB / module_file(text)).is_file():
                return mathlib_page(text)
            return None
        if text in CORE:
            return DOCS_URL + CORE[text].replace('.', '/') + '.html#' + text
        return self.declaration(text, doc_dir)

    def link(self, text, doc_dir):
        """The link target for `text` in a document of `doc_dir`, or None."""
        target = self.target(text, doc_dir)
        if target is None or target.startswith('https:'):
            return target
        path, _, anchor = target.partition('#')
        relative = os.path.relpath(ROOT / path, ROOT / doc_dir)
        if relative == '.':
            return None
        return relative + ('#' + anchor if anchor else '')

    def token(self, match, doc, doc_dir):
        text, old, span = match.groups()
        if text is not None:
            dest = old[1:-1] if old.startswith('<') else old
            recompute = LINE_LINK.match(dest) or dest == mathlib_page(text) or (
                LIBRARIES and dest.startswith(tuple(LIBRARIES.values())) and IDENT.match(text)) or (
                not dest.startswith(('http:', 'https:', 'mailto:', '#'))
                and (not (ROOT / doc_dir / dest.partition('#')[0]).exists()
                     or private(os.path.join(doc_dir, dest.partition('#')[0]))))
            if not recompute:
                return match.group(0)
            new = self.link(text, doc_dir)
            if new is None:
                local = dest.partition('#')[0]
                if (local and not dest.startswith(('http:', 'https:', 'mailto:'))
                        and private(os.path.join(doc_dir, local))):
                    warn('%s: `%s` is private (not published); its link is removed' % (doc, text))
                else:
                    warn('%s: `%s` names nothing any more; its link is removed' % (doc, text))
                return '`%s`' % text
            return '[`%s`](%s)' % (text, new)
        if span is not None:
            new = self.link(span, doc_dir)
            if new is not None:
                return '[`%s`](%s)' % (span, new)
        return match.group(0)

    def rewrite(self, doc):
        doc_dir = os.path.dirname(doc)
        lines = (ROOT / doc).read_text(encoding='utf-8').split('\n')
        out, block, fence = [], [], None

        def flush():
            # The lines of a paragraph are rewritten together, so that a link may span them.
            if block:
                out.append(TOKEN.sub(lambda m: self.token(m, doc, doc_dir), '\n'.join(block)))
                block.clear()

        for i, line in enumerate(lines):
            marker = FENCE.match(line)
            # A backtick fence's info string has no backticks; otherwise the line is inline code.
            if marker and marker.group(1)[0] == '`' and '`' in line[marker.end():]:
                marker = None
            if fence:
                # Only a fence of the same character, at least as long, closes the block.
                if (marker and marker.group(1)[0] == fence[0] and len(marker.group(1)) >= len(fence)
                        and not line[marker.end():].strip()):
                    fence = None
                out.append(line)
                continue
            if marker:
                flush()
                fence = marker.group(1)
                out.append(line)
                continue
            header = line.startswith('|') and i + 1 < len(lines) and TABLE_RULE.match(lines[i + 1])
            if not line.strip() or line.startswith('#') or header:
                flush()
                out.append(line)
            elif line.startswith('|'):
                flush()
                block.append(line)  # a table row is rewritten on its own
                flush()
            else:
                block.append(line)
        flush()
        return '\n'.join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--check', action='store_true',
                        help='list the files whose links are out of date, and change nothing')
    parser.add_argument('docs', nargs='*', help='Markdown files (default: %s)' % ', '.join(DOCS))
    args = parser.parse_args()
    docs = [os.path.relpath(os.path.abspath(d), ROOT) for d in args.docs] or DOCS
    linker = Linker(*load_locations())
    changed = []
    for doc in docs:
        new = linker.rewrite(doc)
        if new != (ROOT / doc).read_text(encoding='utf-8'):
            changed.append(doc)
            if not args.check:
                (ROOT / doc).write_text(new, encoding='utf-8')
    for doc in changed:
        print(('out of date: ' if args.check else 'updated: ') + doc)
    return 1 if args.check and changed else 0


if __name__ == '__main__':
    sys.exit(main())
