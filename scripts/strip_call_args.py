#!/usr/bin/env python3
"""Delete, at every call site, the arguments of binders that were removed from declarations.

usage: strip_call_args.py [REV] [--dry-run] [--force]

After strip_unused.py (or a manual cleanup) deletes explicit hypotheses from declarations, their
callers still pass the old arguments. This script compares the explicit binders `( … )` of every
theorem, lemma and definition in the working tree with the same declaration at the git revision
REV (default HEAD, the commit that starts the round of removals), and deletes the corresponding
arguments at the call sites in the tracked .lean files. A named argument `(h := …)` for a removed
binder is deleted too.

It edits the call sites whose name it can resolve: written in full, or resolved through the
enclosing `namespace` or a plain `open`, with the arguments on the same line. It lists the others
for manual repair: `@` calls, dot notation on a variable (`h.foo`), a declaration passed as a value,
arguments on the next line, a postfix or index glued to an argument, a local name that may shadow
the declaration, ambiguous names, and every call of a declaration that takes explicit `variable`s,
optional arguments or `_` binders. Calls it cannot resolve at all (dot notation on other terms,
names reached through `open … in`) are left for the rebuild to find. Comments and strings are
never edited. The resolution is textual, so a rare edit can still be wrong; the rebuild and
stmt_diff.py, which compares every statement and definition, catch the ones that matter.

Run it from the project root (the directory of the lakefile), once per round, right after the
binders are removed, against the commit that starts the round (HEAD, the default). It refuses an
older commit, and a second run against the same one, since either would delete further, correct
arguments. Then rebuild, and check the statements with stmt_diff.py. An implicit argument that only
the removed hypothesis determined may have to be given by name at some call sites, as in
`(K := K)`.
"""
import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

ID = r"(?:[^\W\d][\w'!?]*|«[^»]*»)"
NAME = rf"{ID}(?:\.(?:{ID}|\d+))*"
MODS = r"(?:(?:private|protected|noncomputable|nonrec|partial|unsafe|public|meta|scoped|local)\s+)*"
DECL = re.compile(rf"^[ \t]*(?:@\[[^\]]*\]\s*)*{MODS}(theorem|lemma|def|abbrev|opaque|instance|axiom|structure|class|inductive)"
                  rf"\s+({NAME})(\.\{{[^}}]*\}})?", re.M)
SCOPE = re.compile(rf"(?:@\[[^\]]*\]\s*)*{MODS}(namespace|section|mutual|end)\b[ \t]*({NAME})?")
TOKEN = re.compile(rf"(?<![\w'!?.@])(@?)({NAME})")
ARG = re.compile(rf"{NAME}|\d+(?:\.\d+)?")
DOTTED = re.compile(rf"(?<=[)\]⟩}}])\.({ID})|(?<![\w'!?.])\.({ID})")
OPEN_BR, CLOSE_BR = '([{⦃⟨', ')]}⦄⟩'
STOP = {'with', 'at', 'using', 'from', 'then', 'else', 'do', 'by', 'fun', 'show', 'in', 'only',
        'generalizing', 'if', 'match', 'let', 'have', 'calc', 'λ', 'where', 'deriving'}
# Words after which a name starts an application rather than being an argument.
TERM_STARTERS = {'exact', 'apply', 'refine', "refine'", 'use', 'exists', 'specialize', 'convert',
                 'rcases', 'obtain', 'cases', 'induction', 'match', 'if', 'then', 'else', 'return',
                 'from', 'show', 'have', 'let', 'calc', 'using', 'by', 'do', 'fun', 'λ',
                 'exact_mod_cast', 'apply_mod_cast', 'simpa', 'absurd', 'replace', 'suffices',
                 'generalize', 'set', 'nomatch', 'linear_combination', 'linarith', 'nlinarith'}
AFTER_ARG = set(' \t\n' + ')]}⦄⟩,;|$:')


def mask(text):
    """The text with comments and the contents of string literals replaced by spaces."""
    out, i, n = list(text), 0, len(text)
    while i < n:
        if text.startswith('--', i):
            a, j = i, text.find('\n', i)
            j = n if j < 0 else j
            b = j
        elif text.startswith('/-', i):
            a, depth, j = i, 0, i
            while j < n:
                if text.startswith('/-', j):
                    depth, j = depth + 1, j + 2
                elif text.startswith('-/', j):
                    depth, j = depth - 1, j + 2
                    if depth == 0:
                        break
                else:
                    j += 1
            b = j
        elif text[i] == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == '\\' else 1
            a, b, j = i + 1, min(j, n), j + 1
        else:
            i += 1
            continue
        for k in range(a, min(b, n)):
            if out[k] != '\n':
                out[k] = ' '
        i = j
    return ''.join(out)


def scopes(masked):
    """Per line: (namespace prefixes, opened namespaces, explicit `variable`s in scope)."""
    stack, info, in_var, depth, var_indent = [{'ns': '', 'open': set(), 'vars': False}], [], False, 0, 0
    for line in masked.split('\n'):
        m = SCOPE.match(line)
        if m:
            kind, arg = m.groups()
            if kind == 'end':
                if len(stack) > 1:
                    stack.pop()
            else:
                stack.append({'ns': arg or '' if kind == 'namespace' else '', 'open': set(),
                              'vars': False})
        words = line.split()
        if words[:1] == ['open'] and words[-1] != 'in' and all(
                re.fullmatch(NAME, w) and w not in ('scoped', 'hiding', 'renaming', 'private')
                for w in words[1:]):
            stack[-1]['open'] |= set(words[1:])
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if re.match(r'variable\b', stripped):
            in_var, depth, var_indent, line_rest = True, 0, indent, stripped[len('variable'):]
        elif in_var and stripped and indent > var_indent:
            line_rest = line
        else:
            in_var, line_rest = False, ''
        for ch in line_rest:
            if ch in OPEN_BR:
                if ch == '(' and depth == 0:
                    stack[-1]['vars'] = True
                depth += 1
            elif ch in CLOSE_BR:
                depth -= 1
        parts = '.'.join(s['ns'] for s in stack if s['ns']).split('.')
        parts = [p for p in parts if p]
        prefixes = ['.'.join(parts[:k]) for k in range(len(parts), -1, -1)]
        info.append((prefixes, set().union(*[s['open'] for s in stack]),
                     any(s['vars'] for s in stack)))
    return info


def type_text(masked, i):
    """The declaration's type, from offset i (after the top-level `:`) to its `:=`, normalized."""
    depth, j = 0, i
    while j < len(masked):
        ch = masked[j]
        if ch in OPEN_BR:
            depth += 1
        elif ch in CLOSE_BR:
            depth -= 1
        elif depth == 0 and (masked.startswith(':=', j) or masked.startswith(' where', j)
                             or masked.startswith('\n|', j) or DECL.match(masked, j)):
            break
        j += 1
    return ' '.join(masked[i:j].split())


def binders(masked, start):
    """Explicit binder names from `start` to the top-level `:`, whether all are plain, the type."""
    i, depth, group, names, plain = start, 0, None, [], True
    while i < len(masked):
        ch = masked[i]
        if depth == 0 and (ch == ':' or masked.startswith(' where', i) or ch == '|'):
            typ = type_text(masked, i + 1) if masked.startswith(':', i) and not masked.startswith(
                ':=', i) else ''
            return names, plain, typ
        if ch in OPEN_BR:
            if depth == 0:
                group = (ch, i)
            depth += 1
        elif ch in CLOSE_BR:
            depth -= 1
            if depth == 0 and group and group[0] == '(':
                body = masked[group[1] + 1:i]
                head = body.split(':')[0].split()
                if ':=' in body or not head or any(not re.fullmatch(ID, h) or h == '_' for h in head):
                    plain = False
                names.extend(head)
        elif depth == 0 and not ch.isspace():
            plain = False
        i += 1
    return names, plain, ''


def declarations(text):
    """{full name: (explicit binders, plain, private, protected, offset of the name, type)}."""
    masked = mask(text)
    info = scopes(masked)
    decls = {}
    for m in DECL.finditer(masked):
        name = m.group(2)
        prefixes, _, has_vars = info[masked.count('\n', 0, m.start(2))]
        full = name[len('_root_.'):] if name.startswith('_root_.') else '.'.join(
            p for p in (prefixes[0], name) if p)
        names, plain, typ = binders(masked, m.end())
        mods = masked[m.start():m.start(2)].split()
        decls[full] = (names, plain and not has_vars, 'private' in mods, 'protected' in mods,
                       m.start(2), typ)
    return decls


def parse_arg(s, j):
    """(start, end, binder name if named) of the argument at or after j, 'glued', or None."""
    while j < len(s) and s[j] in ' \t':
        j += 1
    if j >= len(s) or s[j] in '\n' + CLOSE_BR + ',;|$:' or s.startswith(':=', j):
        return None
    if s[j] in '(⟨[':
        depth, k = 0, j
        while k < len(s):
            if s[k] in OPEN_BR:
                depth += 1
            elif s[k] in CLOSE_BR:
                depth -= 1
                if depth == 0:
                    break
            k += 1
        if k >= len(s):
            return None
        k += 1
        named = re.match(rf"\(\s*({ID})\s*:=", s[j:k])
        if named:
            return j, k, named.group(1)
    else:
        m = ARG.match(s, j)
        if not m or m.group(0) in STOP:
            return None
        k = m.end()
    while k + 1 < len(s) and s[k] == '.' and re.match(rf"{ID}|\d", s[k + 1]):
        k = re.compile(rf"{ID}|\d+").match(s, k + 1).end()
    if k < len(s) and s[k] not in AFTER_ARG:
        return 'glued'
    return j, k, None


def previous_word(s, i):
    """Whether the name at i starts an application ('ok') or may be an argument ('value')."""
    j = i - 1
    while j >= 0 and s[j] in ' \t\n':
        j -= 1
    if j < 0:
        return 'ok', ''
    if s[j] in CLOSE_BR + '"›':
        return 'value', s[j]
    m = re.search(r"[\w'!?.]+$", s[:j + 1])
    if m:
        word = m.group(0)
        if re.match(r"[^\W\d]", word) and word != '_':
            return ('ok' if word in TERM_STARTERS else 'value'), word
        return 'value', word
    return 'ok', s[j]


def locally_bound(text, name):
    """Whether `name` is bound locally in `text` (a declaration): a binder, `have`, `fun`, a pattern."""
    nm = rf"(?<![\w.'@]){re.escape(name)}(?![\w'])"
    return any(re.search(p, text, re.M) for p in (
        rf"\b(?:have|haveI|let|letI|set|show|obtain)\s+{nm}",
        rf"{nm}\s*:(?!=)",
        rf"\b(?:fun|λ)\b[^=↦\n]*?{nm}",
        rf"(?:∀|∃!?)[^,\n]*?{nm}",
        rf"\b(?:intro|intros|rintro)\b[^\n;]*?{nm}",
        rf"\b(?:rcases|obtain|cases|induction|match)\b[^\n]*?\bwith\b[^\n]*?{nm}",
        rf"\bobtain\s*⟨[^⟩\n]*{nm}",
        rf"^\s*\|[^=\n]*?{nm}[^\n]*=>",
        rf"\bchoose\b[^\n]*?{nm}[^\n]*\busing\b"))


def edit_file(path, text, changes, all_full):
    """Deletions for `changes` ({full name: (old binders, removed, plain, protected)}) in a file.

    Returns the new text, the number of edited call sites per name, and the manual reports."""
    masked = mask(text)
    info = scopes(masked)
    lines = text.split('\n')
    decl_matches = list(DECL.finditer(masked))
    headers = {m.start(2) for m in decl_matches}
    decl_starts = [m.start() for m in decl_matches] + [len(masked)]
    shadowed = {}

    def bound_here(pos, short):
        k = max((i for i, a in enumerate(decl_starts[:-1]) if a <= pos), default=None)
        if k is None:
            return False
        if (k, short) not in shadowed:
            shadowed[(k, short)] = locally_bound(masked[decl_starts[k]:decl_starts[k + 1]], short)
        return shadowed[(k, short)]
    by_short = {}
    for full in changes:
        by_short.setdefault(full.split('.')[-1], []).append(full)
    spans, manual, fixed = [], [], {}

    def report(pos, why):
        ln = masked.count('\n', 0, pos)
        manual.append(f'{path}:{ln + 1}: {why}: {lines[ln].strip()[:90]}')

    for m in DOTTED.finditer(masked):
        if (m.group(1) or m.group(2)) in by_short:
            report(m.start(), 'dot notation')
    for m in TOKEN.finditer(masked):
        at, written = m.groups()
        short = written.split('.')[-1]
        if short not in by_short or m.start(2) in headers:
            continue
        ln = masked.count('\n', 0, m.start())
        if lines[ln].lstrip().startswith(('#check', '#print', 'attribute', 'export', 'open')):
            continue
        prefixes, opened, _ = info[ln]
        if written.startswith('_root_.'):
            cands = {written[len('_root_.'):]}
        else:
            cands = {'.'.join(x for x in (p, written) if x) for p in prefixes}
            cands |= {f'{o}.{written}' for o in opened}
        targets = [f for f in by_short[short] if f in cands]
        if not targets:
            if '.' in written and written[0].islower() and not cands & all_full:
                report(m.start(), 'possible dot notation')
            continue
        full = targets[0]
        old, removed, plain, protected = changes[full]
        if '.' not in written and bound_here(m.start(), short):
            report(m.start(), 'a local name may shadow the declaration')
            continue
        if len(targets) > 1 or any(f in cands for f in all_full - set(changes)) or (
                protected and '.' not in written):
            report(m.start(), 'ambiguous name')
            continue
        if at:
            report(m.start(), '`@` call')
            continue
        if not plain:
            report(m.start(), 'call of a declaration with explicit `variable`s, optional or `_` binders')
            continue
        kind, word = previous_word(masked, m.start())
        if kind == 'value':
            report(m.start(), f'may be passed as a value (after `{word}`)')
            continue
        pos, positional, named, glued = m.end(2), [], [], False
        while len(positional) < len(old):
            a = parse_arg(masked, pos)
            if a is None or a == 'glued':
                glued = a == 'glued'
                break
            pos = a[1]
            (named if a[2] is not None else positional).append(a)
        given = {a[2] for a in named}
        slots = [b for b in old if b not in given]
        need = [slots.index(r) for r in removed if r not in given]
        if need and len(positional) <= max(need):
            if not positional and not named and masked[m.end(2):m.end(2) + 1] in ',])⟩}':
                continue
            report(m.start(), 'postfix or index glued to an argument' if glued else
                   'arguments not all on this line')
            continue
        for a0, a1, _ in [a for a in named if a[2] in removed] + [positional[i] for i in need]:
            while a0 > 0 and text[a0 - 1] in ' \t':
                a0 -= 1
            spans.append((a0, a1))
        fixed[full] = fixed.get(full, 0) + 1
    kept = []
    for a, b in sorted(spans, key=lambda s: (s[0], -s[1])):
        if kept and b <= kept[-1][1]:
            continue
        kept.append((a, b))
    out = text
    for a, b in reversed(kept):
        out = out[:a] + out[b:]
    return out, fixed, manual


def git(*args, check=True):
    r = subprocess.run(['git', *args], capture_output=True, text=True)
    if check and r.returncode != 0:
        sys.exit(f'git {" ".join(args)}: {r.stderr.strip()}')
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog='\n\n'.join(__doc__.split('\n\n')[2:]))
    ap.add_argument('rev', nargs='?', default='HEAD',
                    help='the commit before the binders were removed (default: HEAD)')
    ap.add_argument('--dry-run', action='store_true', help='show the edits without making them')
    ap.add_argument('--force', action='store_true',
                    help='run against a commit other than HEAD, or again against the same one')
    args = ap.parse_args()
    if not (Path('lakefile.toml').is_file() or Path('lakefile.lean').is_file()):
        sys.exit('run from the project root, the directory of the lakefile')
    git('rev-parse', '--is-inside-work-tree')
    rev = git('rev-parse', '--verify', '--quiet', f'{args.rev}^{{commit}}', check=False)
    if rev.returncode:
        sys.exit(f'not a commit: {args.rev}')
    rev = rev.stdout.strip()
    if not args.dry_run and not args.force and rev != git('rev-parse', 'HEAD').stdout.strip():
        sys.exit(f'{args.rev} is not HEAD. Run against the commit that starts this round (the '
                 'default): an older commit would make it edit call sites that earlier rounds '
                 'fixed. Pass --force to override.')
    marker = Path(git('rev-parse', '--git-path', 'strip_call_args.done').stdout.strip())
    if not args.dry_run and not args.force and marker.is_file() and marker.read_text().strip() == rev:
        sys.exit(f'already run against {args.rev} ({rev[:12]}): its call sites were edited once. '
                 'Commit the round before the next one. If you reset the working tree to redo '
                 'this round, pass --force.')
    files = [p for p in git('ls-files', '-z', '--', '*.lean').stdout.split('\0')
             if p and Path(p).is_file()]
    texts, new, old = {}, {}, {}
    for f in files:
        texts[f] = Path(f).read_text(encoding='utf-8')
        for full, d in declarations(texts[f]).items():
            new[(f, full) if d[2] else full] = d + (f,)
        before = git('show', f'{args.rev}:./{f}', check=False)
        if before.returncode == 0:
            for full, d in declarations(before.stdout).items():
                old[(f, full) if d[2] else full] = d
    changes, status = {}, 0
    for key, (names, plain, private, protected, _pos, typ, home) in new.items():
        if key not in old or old[key][0] == names:
            continue
        full, old_names = (key[1] if private else key), old[key][0]
        removed = [b for b in old_names if b not in names]
        if len(set(old_names)) < len(old_names):
            print(f'{full}: explicit binders with repeated names (such as `_`); not handled')
            status = 1
        elif not removed or [b for b in old_names if b in names] != names:
            print(f'{full}: explicit binders changed other than by deletion; not handled')
            status = 1
        elif typ != old[key][5]:
            print(f'{full}: explicit binders and type changed together; not handled')
            status = 1
        else:
            changes[key] = (full, home, (old_names, removed, plain and old[key][1], protected))
    if not changes:
        print('no declaration lost an explicit binder since', args.rev)
        return status
    all_full = {k[1] if isinstance(k, tuple) else k for k in new}
    total, edited = {}, False
    for f in files:
        local = {full: c for key, (full, home, c) in changes.items()
                 if not isinstance(key, tuple) or home == f}
        out, fixed, manual = edit_file(f, texts[f], local, all_full)
        for full, n in fixed.items():
            total[full] = total.get(full, 0) + n
        for line in manual:
            print('  MANUAL', line)
            status = 1
        if out != texts[f]:
            if args.dry_run:
                sys.stdout.writelines(difflib.unified_diff(
                    texts[f].splitlines(True), out.splitlines(True), f, f + ' (edited)', n=0))
            else:
                Path(f).write_text(out, encoding='utf-8')
                edited = True
    if edited:
        marker.write_text(rev + '\n')
    for full, _home, (_old, removed, _plain, _prot) in changes.values():
        verb = 'would drop' if args.dry_run else 'dropped'
        print(f'{full}: {verb} argument(s) {", ".join(removed)} at {total.get(full, 0)} call site(s)')
    return status


if __name__ == '__main__':
    sys.exit(main())
