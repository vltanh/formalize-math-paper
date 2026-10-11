#!/usr/bin/env python3
"""Check that each formal proof follows the route of the paper's proof.

The *route* of a proof is the set of numbered results of the paper that it uses. For the paper,
these are the results that the proof cites (`\\cref`, `\\Cref`, `\\ref`, `\\autoref`); for the
formalization, the numbered results that the Lean proof reaches through the library's helper
lemmas, which `scripts/Audit.lean` (from the skill's `assets/`) writes to `.lake/route_deps.tsv`.
A formal proof that follows the paper's argument cites the same results. Every difference is
either a proof to fix or a departure from the paper to record.

    route_check.py extract main.tex [MORE.tex | DIR ...] > docs/paper_routes.tsv
    route_check.py check docs/paper_routes.tsv [--deps .lake/route_deps.tsv]
                         [--accept docs/route_differences.tsv]

`extract` reads the TeX source, following `\\input` and `\\include` from each file given (a
directory stands for its `.tex` files in sorted order), and writes one line per labelled
statement of a theorem-like environment: its label, its environment, whether the paper proves it
(1 or 0), and the labels of the statements that its proof cites. A proof belongs to:

- the statement named first in its optional argument (`\\begin{proof}[Proof of \\Cref{thm:a}]`,
  with or without a space before the bracket); the other statements named there (`[Proof of
  Theorem~\\ref{a} using Lemma~\\ref{b}]`) count as cited;
- otherwise, the statement that the sentence just before it names as the one being proved
  ("We now finish the proof of Lemma~\\ref{a}.");
- otherwise, the closest statement before it, unless a section heading separates them. An
  unlabelled statement that restates a labelled one, numbered after it
  (`\\def\\thetheorem{\\ref{a}}` before it, or `\\ref{a}` in its title), stands for that one.

The two heuristics, and every proof that cannot be attributed, are reported on standard error:
check them against the paper. The output contains only labels, so it can be committed even when
the TeX source cannot be. It covers statements and their proof environments only: a result
proved in running text, or a labelled equation that the paper treats as a result, needs a row
added by hand, with a `#` comment line that says why.

`check` maps each Lean result to the first code span of its docstring that is a label of the
paper (write the label in backticks in the docstring of every numbered result), and compares the
two routes of every result that the paper proves:

- `-X`: the paper's proof cites X, and the Lean proof never reaches X, not even through the
  results it uses: it avoids a step of the paper's argument;
- `+X`: the Lean proof uses X, and the paper's argument does not reach X, not even through the
  results its proof cites.

A difference that the other route explains is not reported (`--all` shows it too): a cited result
that the Lean proof reaches through another result, or a result that the Lean proof uses directly
where the paper reaches it through a cited result. Each reported difference must be reviewed. Either the Lean proof is changed to follow the paper, or the
difference is recorded in the accept file, one line per difference, `LABEL<TAB>±OTHER<TAB>reason`
(lines starting with `#` are comments): for example a departure from the paper's proof, which is
also reported in the docstring and in the report, or a result that the paper's proof uses without
citing it. `*<TAB>+OTHER<TAB>reason` records a result that the paper uses without citing it
throughout, such as a basic property of its objects. The command exits with status 1 if a difference is not in the accept file, or if an
entry of the accept file no longer describes a difference.
"""

import argparse
import os
import re
import signal
import sys

STATEMENT_ENVS = ('theorem', 'lemma', 'proposition', 'corollary', 'claim', 'fact', 'observation',
                  'conjecture', 'example')
REF = re.compile(r'\\(?:[cC]ref|ref|autoref|labelcref|namecref|nameCref)\*?\{([^}]*)\}')
# A restatement numbered after its original: `\def\thetheorem{\ref{a}}`, `\renewcommand{\thetheorem}{…}`.
RESTATE = re.compile(r'\\(?:def|renewcommand\*?)\s*\{?\\the[A-Za-z]+\}?\s*\{[^{}]*?'
                     r'\\(?:[cC]ref|ref|autoref)\*?\{([^}]*)\}')
# A sectioning command: a proof after one is not attributed to a statement before it.
SECTION = re.compile(r'\\(?:chapter|section|subsection|subsubsection)\*?\s*[\[{]')
# A sentence that introduces a proof by naming the result it proves.
PROOF_OF = re.compile(r'[Pp]roof\s+of\s+[^.;:\n]{0,60}?\\(?:[cC]ref|ref|autoref)\*?\{([^},]*)')
INPUT = re.compile(r'\\(?:input|include)\{([^}]*)\}')


def strip_comments(text):
    return re.sub(r'(?<!\\)%.*', '', text)


def read_tex(path, roots, seen):
    """The text of a TeX file with its \\input and \\include expanded."""
    path = os.path.normpath(path)
    if path in seen or not os.path.isfile(path):
        return ''
    seen.add(path)
    text = strip_comments(open(path, encoding='utf-8', errors='replace').read())

    def expand(m):
        name = m.group(1).strip()
        cands = [name] if name.endswith('.tex') else [name + '.tex', name]
        for base in [os.path.dirname(path)] + roots:
            for c in cands:
                p = os.path.join(base, c)
                if os.path.isfile(p):
                    return read_tex(p, roots, seen)
        return ''
    return INPUT.sub(expand, text)


def gather(paths):
    out, seen = [], set()
    for p in paths:
        if os.path.isdir(p):
            files = sorted(os.path.join(dp, f) for dp, _, fs in os.walk(p) for f in fs
                           if f.endswith('.tex'))
            for f in files:
                out.append(read_tex(f, [p], seen))
        else:
            out.append(read_tex(p, [os.path.dirname(p) or '.'], seen))
    return '\n'.join(out)


def extract(text, warn=lambda msg: None):
    """For each labelled statement: its environment, whether it is proved, and what the proof cites.
    `warn` receives a message for every heuristic attribution and every proof left unattributed."""
    envs = '|'.join(STATEMENT_ENVS)
    token = re.compile(r'\\begin\{(%s)\*?\}|\\end\{(%s)\*?\}|\\begin\{proof\}(\s*\[[^\]]*\])?'
                       r'|\\end\{proof\}' % (envs, envs))
    statements = {}            # label -> [env, proved, set of cited labels]
    order = []
    current = None             # label of the last statement seen
    current_end = 0            # where that statement ends
    in_statement = None        # (env, start of its body, start of its \begin) while inside a statement
    proof_owner, proof_start, proof_cited, depth = None, None, set(), 0
    last_end = 0               # end of the last statement or proof: the text after it introduces a proof

    def snippet(i):
        return ' '.join(text[i:i + 60].split())

    for m in token.finditer(text):
        if m.group(1):                                   # \begin{theorem}
            if depth == 0:
                in_statement = (m.group(1), m.end(), m.start())
        elif m.group(2):                                 # \end{theorem}
            if in_statement and depth == 0:
                body = text[in_statement[1]:m.start()]
                lab = re.search(r'\\label\{([^}]*)\}', body)
                current_end = m.end()
                if lab:
                    current = lab.group(1).strip()
                    if current not in statements:
                        statements[current] = [in_statement[0], 0, set()]
                        order.append(current)
                    elif statements[current][0] == '?':      # first seen through a restatement
                        statements[current][0] = in_statement[0]
                else:
                    # an unlabelled restatement of a labelled statement, numbered after it
                    before = text[max(last_end, in_statement[2] - 300):in_statement[2]]
                    title = re.match(r'\s*\[([^\]]*)\]', body)
                    refs = (REF.findall(title.group(1)) if title else []) or RESTATE.findall(before)
                    current = refs[-1].split(',')[0].strip() if refs else None
                    if current:
                        warn(f'an unlabelled {in_statement[0]} is read as a restatement of {current}: '
                             f'{snippet(in_statement[1])}')
                last_end = m.end()
            in_statement = None
        elif m.group(0).startswith('\\begin{proof}'):
            depth += 1
            if depth == 1:
                owner, cited = current, set()
                opt = m.group(3)
                refs = [r.strip() for g in REF.findall(opt or '') for r in g.split(',') if r.strip()]
                if refs:
                    owner, cited = refs[0], set(refs[1:])
                else:
                    intro = PROOF_OF.findall(text[max(last_end, m.start() - 400):m.start()])
                    if intro and intro[-1].strip() != owner:
                        warn(f'a proof is attributed to {intro[-1].strip()}, which the sentence before it '
                             f'names, rather than to {owner}: {snippet(m.end())}')
                        owner = intro[-1].strip()
                    elif owner is not None and SECTION.search(text[current_end:m.start()]):
                        warn(f'a proof is separated by a section heading from {owner}, the closest statement '
                             f'before it, and is not attributed: {snippet(m.end())}')
                        owner = None
                    elif owner is None:
                        warn(f'a proof follows no labelled statement and is not attributed: '
                             f'{snippet(m.end())}')
                proof_owner, proof_start, proof_cited = owner, m.end(), cited
        else:                                            # \end{proof}
            depth = max(0, depth - 1)
            if depth == 0:
                if proof_owner is not None:
                    body = text[proof_start:m.start()]
                    cited = {r.strip() for g in REF.findall(body) for r in g.split(',') if r.strip()}
                    entry = statements.setdefault(proof_owner, ['?', 0, set()])
                    if proof_owner not in order:
                        order.append(proof_owner)
                    entry[1] = 1
                    entry[2] |= cited | proof_cited
                proof_owner = None
                last_end = m.end()
    # keep only citations of statements
    for lab in order:
        statements[lab][2] = {c for c in statements[lab][2] if c in statements and c != lab}
    return order, statements


def load_paper(path):
    paper = {}
    for line in open(path, encoding='utf-8'):
        if not line.strip() or line.startswith('#'):
            continue
        parts = line.rstrip('\n').split('\t') + ['']
        label, env, proved, cited = parts[0], parts[1], parts[2], parts[3]
        paper[label] = (env, proved == '1', {c for c in cited.split(',') if c})
    return paper


def load_deps(path, paper):
    """Lean result -> (label, used Lean results); the label is the first docstring code span that
    is a label of the paper."""
    lean = {}
    for line in open(path, encoding='utf-8'):
        if not line.strip():
            continue
        parts = line.rstrip('\n').split('\t') + ['', '', '']
        _, name, labels, uses = parts[0], parts[1], parts[2], parts[3]
        label = next((l for l in labels.split(',') if l in paper), None)
        lean[name] = (label, [u for u in uses.split(',') if u])
    return lean


def load_accept(path):
    accept = {}
    if not path or not os.path.isfile(path):
        return accept
    for n, line in enumerate(open(path, encoding='utf-8'), 1):
        if not line.strip() or line.startswith('#'):
            continue
        parts = line.rstrip('\n').split('\t')
        if len(parts) < 3 or not parts[1][:1] in '+-' or not parts[2].strip():
            sys.exit(f'{path}:{n}: expected LABEL<TAB>+OTHER or -OTHER<TAB>reason')
        if parts[0] == '*' and parts[1].startswith('-'):
            sys.exit(f'{path}:{n}: `*` records a result used without citation (+OTHER); '
                     'record each -OTHER for its own result')
        accept[(parts[0], parts[1])] = parts[2].strip()
    return accept


def check(args):
    paper = load_paper(args.paper)
    lean = load_deps(args.deps, paper)
    accept = load_accept(args.accept)
    by_label = {}
    unlabelled = []
    for name, (label, uses) in lean.items():
        if label is None:
            unlabelled.append(name)
            continue
        by_label.setdefault(label, set())
        for u in uses:
            ul = lean.get(u, (None,))[0]
            if ul and ul != label:
                by_label[label].add(ul)
    paper_graph = {label: cited for label, (env, proved, cited) in paper.items()}

    def closure(graph, start):
        seen, stack = set(), list(graph.get(start, ()))
        while stack:
            x = stack.pop()
            if x not in seen:
                seen.add(x)
                stack.extend(graph.get(x, ()))
        return seen

    diffs, accepted, weak = [], [], []
    used_keys = set()
    for label, (env, proved, cited) in paper.items():
        if not proved or label not in by_label:
            continue
        used = by_label[label]
        lean_reach, paper_reach = closure(by_label, label), closure(paper_graph, label)
        for kind, others, reach in (('-', cited - used, lean_reach), ('+', used - cited, paper_reach)):
            for o in sorted(others):
                d = kind + o
                if o in reach and not args.all:
                    weak.append((label, d))
                    continue
                key = (label, d) if (label, d) in accept else ('*', d)
                if key in accept and (kind == '+' or key[0] != '*'):
                    accepted.append((label, d))
                    used_keys.add(key)
                else:
                    diffs.append((label, d))
    stale = [k for k in accept if k not in used_keys]
    unproved = sorted(l for l, (e, p, c) in paper.items() if not p and l in by_label)
    unformalized = sorted(l for l, (e, p, c) in paper.items() if l not in by_label)

    print(f'{len(by_label)} results of the paper found in the Lean code; '
          f'{len(diffs) + len(accepted)} route differences, {len(accepted)} of them recorded'
          + ('' if args.all else f'; {len(weak)} more that the other route explains (--all)') + '.')
    if diffs:
        print('\nTo review (fix the Lean proof, or record the difference and its reason):')
        for label, d in diffs:
            what = ('the paper\'s proof cites %s; the Lean proof does not use it' if d[0] == '-'
                    else 'the Lean proof uses %s; the paper\'s proof does not cite it') % d[1:]
            print(f'  {label}\t{d}\t{what}')
    if stale:
        print('\nRecorded differences that no longer occur (remove them from the accept file):')
        for label, d in stale:
            print(f'  {label}\t{d}')
    if args.verbose:
        if accepted:
            print('\nRecorded differences:')
            for label, d in accepted:
                reason = accept.get((label, d)) or accept.get(('*', d))
                print(f'  {label}\t{d}\t{reason}')
        if unproved:
            print('\nStated without proof in the paper (no route to compare):', ', '.join(unproved))
        if unformalized:
            print('\nStatements of the paper with no Lean result naming their label:',
                  ', '.join(unformalized))
        if unlabelled:
            print('\nLean results whose docstring names no label of the paper:',
                  ', '.join(sorted(unlabelled)))
    return 1 if (diffs or stale) else 0


def main():
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = ap.add_subparsers(dest='cmd', required=True)
    ex = sub.add_parser('extract', help='the routes of the paper\'s proofs, from the TeX source')
    ex.add_argument('tex', nargs='+')
    ch = sub.add_parser('check', help='compare them with the routes of the Lean proofs')
    ch.add_argument('paper')
    ch.add_argument('--deps', default='.lake/route_deps.tsv')
    ch.add_argument('--accept')
    ch.add_argument('--all', action='store_true',
                    help='also report the differences that the other route explains')
    ch.add_argument('-v', '--verbose', action='store_true')
    args = ap.parse_args()
    if args.cmd == 'extract':
        order, statements = extract(gather(args.tex),
                                    warn=lambda msg: print('warning: ' + msg, file=sys.stderr))
        print('# label\tenvironment\tproved\tcited statements (from route_check.py extract)')
        for lab in order:
            env, proved, cited = statements[lab]
            print(f'{lab}\t{env}\t{proved}\t{",".join(sorted(cited))}')
        return 0
    return check(args)


if __name__ == '__main__':
    sys.exit(main())
