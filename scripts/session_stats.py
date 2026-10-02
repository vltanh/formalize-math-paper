#!/usr/bin/env python3
"""Summarize a Claude Code session: elapsed time, models, sub-agents and their effort.

usage: session_stats.py [TRANSCRIPT.jsonl] [--until ISO-TIME]

Claude Code keeps each session's transcript in
~/.claude/projects/<project path, with every "/" replaced by "-">/<session id>.jsonl.
Without an argument, the script reads the most recently modified transcript of the project in the
current directory. It prints:

- the first and last timestamps, and the elapsed time between them;
- the models and Claude Code versions that appear;
- the number of sub-agents launched, the largest number running at the same time, and how often a
  finished sub-agent was resumed;
- the working time, tokens and tool calls that the sub-agents reported when they finished, summed
  over all their runs.

With --until (for example the time of the commit that completed the formalization, as printed by
`git log -1 --format=%cI <commit>`), only events up to that time count.

These are the figures the README's credits and `formalization.yaml`'s `automation` section report.
Agents other than Claude Code keep the same figures by hand in the run log (see SKILL.md).
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

LAUNCH = re.compile(r'agentId: ([A-Za-z0-9]+)')
RESUME = re.compile(r'Resuming agent ([A-Za-z0-9]+)')
TASK = re.compile(r'<task-id>([A-Za-z0-9]+)</task-id>')
STATUS = re.compile(r'<status>(\w+)</status>')
USAGE = re.compile(r'<subagent_tokens>(\d+)</subagent_tokens>\s*<tool_uses>(\d+)</tool_uses>\s*'
                   r'<duration_ms>(\d+)</duration_ms>')


def parse_time(s):
    return datetime.fromisoformat(s.replace('Z', '+00:00'))


def default_transcript():
    key = str(Path.cwd()).replace('/', '-')
    folder = Path.home() / '.claude' / 'projects' / key
    files = sorted(folder.glob('*.jsonl'), key=lambda p: p.stat().st_mtime)
    if not files:
        sys.exit(f'no transcript in {folder}; pass the path of one')
    return files[-1]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('transcript', nargs='?')
    ap.add_argument('--until', help='ignore events after this ISO 8601 time')
    args = ap.parse_args()
    path = Path(args.transcript) if args.transcript else default_transcript()
    until = parse_time(args.until) if args.until else None

    first = last = None
    models, versions = {}, set()
    launched, resumes, ends, usage = {}, [], {}, set()
    for line in path.read_text(encoding='utf-8').splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = rec.get('timestamp')
        if not ts:
            continue
        t = parse_time(ts)
        if until and t > until:
            continue
        first = first or t
        last = t
        if rec.get('version'):
            versions.add(rec['version'])
        msg = rec.get('message')
        if rec.get('type') == 'assistant':
            if isinstance(msg, dict) and msg.get('model'):
                models[msg['model']] = models.get(msg['model'], 0) + 1
            continue
        for m in LAUNCH.finditer(line):
            launched.setdefault(m.group(1), t)
        for m in RESUME.finditer(line):
            resumes.append((t, m.group(1)))
        tasks = TASK.findall(line)
        if tasks and any(s in ('completed', 'failed', 'killed') for s in STATUS.findall(line)):
            for task in tasks:
                ends.setdefault(task, []).append(t)
            for m in USAGE.finditer(line):
                usage.add((tasks[0],) + tuple(int(x) for x in m.groups()))

    if first is None:
        sys.exit('no timestamped records')
    intervals = []
    for agent, t0 in launched.items():
        stop = min((e for e in ends.get(agent, []) if e > t0), default=last)
        intervals.append((t0, stop))
    for t0, prefix in resumes:
        agent = next((a for a in launched if a.startswith(prefix)), None)
        if agent:
            stop = min((e for e in ends.get(agent, []) if e > t0), default=last)
            intervals.append((t0, stop))
    events = sorted([(a, 1) for a, _ in intervals] + [(b, -1) for _, b in intervals])
    running = peak = 0
    for _, d in events:
        running += d
        peak = max(peak, running)

    hours = (last - first).total_seconds() / 3600
    agent_ms = sum(u[3] for u in usage)
    print(f'transcript:          {path}')
    print(f'first / last event:  {first.isoformat()}  /  {last.isoformat()}')
    print(f'elapsed:             {hours:.2f} h')
    print(f'models:              ' + ', '.join(f'{m} ({n} messages)' for m, n in models.items()))
    print(f'Claude Code:         ' + ', '.join(sorted(versions)))
    print(f'sub-agents launched: {len(launched)}  (at most {peak} at once; {len(resumes)} resumptions)')
    print(f'sub-agent work:      {agent_ms / 3.6e6:.1f} h, {sum(u[1] for u in usage):,} tokens, '
          f'{sum(u[2] for u in usage):,} tool calls (as reported when they finished)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
