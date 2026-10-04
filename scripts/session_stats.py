#!/usr/bin/env python3
"""Summarize Claude Code sessions for the run log: elapsed time, models, sub-agents and effort.

usage: session_stats.py [TRANSCRIPT.jsonl …] [--since TIME] [--until TIME]

Claude Code keeps each session's transcript in
~/.claude/projects/<project path, every character but letters and digits replaced by "-">/<id>.jsonl
and the transcripts of its sub-agents, workflow agents included, under <id>/subagents/. Without an
argument, the script reads the most recently modified transcript of the project in the current
directory. Pass every transcript when the work spanned several sessions.

It prints:

- the first and last event, and the elapsed time between them;
- the models (API calls per model) and the Claude Code versions;
- the number of sub-agents, the largest number running at the same time, and how often a finished
  sub-agent was resumed;
- the work of the sub-agents and of the main session: the sub-agents' working time (the wall time
  of each run, summed), tool calls, and tokens, split into output, input (uncached input and cache
  writes) and cache reads.

The figures come from the transcripts themselves. The usage line that Claude Code shows when a
sub-agent finishes is not a measure of work: its token count is the size of the agent's context at
the end, and after a resume it may or may not include the earlier run.

With --until (ISO 8601; local time if it has no time zone), only events up to that time count: for
example the time of the commit that completed the formalization, from
`git log -1 --format=%cI <commit>`. With --since, only events from that time on count: together,
the two give the figures of one round of work, such as a later round that the user asked for.
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def parse_time(s):
    t = datetime.fromisoformat(s.replace('Z', '+00:00'))
    return t if t.tzinfo else t.astimezone()


def default_transcript():
    key = re.sub(r'[^A-Za-z0-9]', '-', str(Path.cwd()))
    folder = Path.home() / '.claude' / 'projects' / key
    files = sorted(folder.glob('*.jsonl'), key=lambda p: p.stat().st_mtime)
    if not files:
        sys.exit(f'no transcript in {folder}; pass the path of one')
    return files[-1]


def records(path, since, until):
    """(time, record) for every timestamped record from `since` to `until`, in time order."""
    out = []
    for line in path.open(encoding='utf-8'):
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(r, dict) or not r.get('timestamp'):
            continue
        t = parse_time(r['timestamp'])
        if (since is None or t >= since) and (until is None or t <= until):
            out.append((t, r))
    out.sort(key=lambda x: x[0])
    return out


class Usage:
    """API calls, tool calls and tokens of the assistant messages fed to `add`."""

    def __init__(self):
        self.calls, self.tools, self.models = {}, set(), {}

    def add(self, r):
        m = r.get('message')
        if r.get('type') != 'assistant' or not isinstance(m, dict):
            return
        mid = m.get('id') or r.get('uuid')
        self.calls[mid] = m.get('usage') or {}
        if m.get('model') and m['model'] != '<synthetic>':
            self.models.setdefault(m['model'], set()).add(mid)
        for c in m.get('content') or []:
            if isinstance(c, dict) and c.get('type') == 'tool_use':
                self.tools.add(c.get('id') or (mid, len(self.tools)))

    def merge(self, other):
        self.calls.update(other.calls)
        self.tools |= other.tools
        for k, v in other.models.items():
            self.models.setdefault(k, set()).update(v)

    def tokens(self):
        u = self.calls.values()
        return (sum(x.get('output_tokens') or 0 for x in u),
                sum((x.get('input_tokens') or 0) + (x.get('cache_creation_input_tokens') or 0)
                    for x in u),
                sum(x.get('cache_read_input_tokens') or 0 for x in u))


def is_prompt(r):
    """A message that starts or resumes a sub-agent's work, as opposed to a tool result or the
    summary that a context compaction inserts. The time before a prompt is idle."""
    if r.get('type') != 'user' or r.get('isCompactSummary'):
        return False
    c = (r.get('message') or {}).get('content')
    if isinstance(c, str):
        return True
    return isinstance(c, list) and any(isinstance(b, dict) and b.get('type') == 'text' for b in c) \
        and not any(isinstance(b, dict) and b.get('type') == 'tool_result' for b in c)


def fmt_tokens(t):
    out, inp, cache = t
    return f'{out / 1e6:.2f}M output, {inp / 1e6:.2f}M input, {cache / 1e6:,.0f}M cache reads'


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter,
                                 epilog='\n\n'.join(__doc__.split('\n\n')[1:]))
    ap.add_argument('transcripts', nargs='*', metavar='TRANSCRIPT')
    ap.add_argument('--since', help='ignore events before this ISO 8601 time')
    ap.add_argument('--until', help='ignore events after this ISO 8601 time')
    args = ap.parse_args()
    paths = list(dict.fromkeys(Path(p).resolve() for p in args.transcripts)) or [default_transcript()]
    for p in paths:
        if not p.is_file():
            sys.exit(f'no such transcript: {p}')
    since = parse_time(args.since) if args.since else None
    until = parse_time(args.until) if args.until else None

    first = last = None
    versions, main_usage, agent_usage = set(), Usage(), Usage()
    launched, resumed, runs, agents = set(), set(), [], 0
    for path in paths:
        recs = records(path, since, until)
        if not recs:
            continue
        first = min(first or recs[0][0], recs[0][0])
        last = max(last or recs[-1][0], recs[-1][0])
        for t, r in recs:
            if r.get('version'):
                versions.add(r['version'])
            main_usage.add(r)
            res = r.get('toolUseResult')
            if isinstance(res, dict):
                if res.get('agentId') and res.get('status') in ('async_launched', 'completed'):
                    launched.add(res['agentId'])
                if res.get('resumedAgentId'):
                    resumed.add(r.get('uuid') or (t, res['resumedAgentId']))
        for f in sorted(path.with_suffix('').glob('subagents/**/agent-*.jsonl')):
            recs = records(f, since, until)
            if not recs:
                continue
            agents += 1
            usage = Usage()
            start = prev = recs[0][0]
            for t, r in recs:
                if r.get('version'):
                    versions.add(r['version'])
                usage.add(r)
                if is_prompt(r) and t > start:
                    runs.append((start, prev))
                    start = t
                prev = t
            runs.append((start, prev))
            agent_usage.merge(usage)
    if first is None:
        sys.exit('no timestamped records')
    if launched and not agents:
        print('warning: no sub-agent transcripts found next to the session transcript(s); '
              'the sub-agent figures below are missing', file=sys.stderr)

    running = peak = 0
    for _, d in sorted([(a, 1) for a, _ in runs] + [(b, -1) for _, b in runs]):
        running += d
        peak = max(peak, running)
    hours = (last - first).total_seconds() / 3600
    work = sum((b - a).total_seconds() for a, b in runs) / 3600
    models = sorted(set(main_usage.models) | set(agent_usage.models))
    print('transcripts:         ' + ', '.join(str(p) for p in paths))
    print(f'first / last event:  {first.isoformat()}  /  {last.isoformat()}')
    print(f'elapsed:             {hours:.2f} h')
    print('models (API calls):  ' + ', '.join(
        f'{m} ({len(main_usage.models.get(m, ()))} main, {len(agent_usage.models.get(m, ()))} sub-agents)'
        for m in models))
    print('Claude Code:         ' + ', '.join(sorted(versions)))
    print(f'sub-agents:          {agents} ({len(launched)} launched by the main session; '
          f'at most {peak} running at once; {len(resumed)} resumptions)')
    print(f'sub-agent work:      {work:.1f} h, {len(agent_usage.tools):,} tool calls; tokens: '
          + fmt_tokens(agent_usage.tokens()))
    print(f'main session:        {len(main_usage.tools):,} tool calls; tokens: '
          + fmt_tokens(main_usage.tokens()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
