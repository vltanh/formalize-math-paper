# Follow-up papers: `notes/follow-up-papers.md`

## Contents

1. What it is for
2. Finding candidates
3. The bar: a paper, not a remark
4. Exploring a candidate
5. Checking
6. Structure of the follow-up file
7. Keeping it private

## 1. What it is for

The follow-up file, `notes/follow-up-papers.md` in the project's private notes (with several
papers, `notes/PaperName/follow-up-papers.md`; `multi-paper.md`, Section 6), answers one question
for the user: what paper could they write next, following this one? The report's Section 11
records what the work showed about the paper: hypotheses it does not need, variants its proofs
cover, simpler arguments, extensions of the formalization. These are worth having, but most of them
make a remark in a revised version, not a paper. The follow-up file is for the directions that
would make a paper of their own, explored far enough that the user can judge whether to spend
months on one.

Formalizing the paper gave you the most thorough reading it will get. You know which hypothesis
each step uses, which estimates are tight and which have room, which steps are generic and which
depend on the special structure, and where the paper's own remarks about its method are right or
wrong. Use that knowledge. A list of directions that anyone could write from the abstract adds
nothing.

For a project formalized before this step existed, or when the user asks for it on its own, start
from the project's `docs/PaperName/REPORT.md`, its inventory if it kept one, the paper's TeX source
and the Lean library, and refresh the literature search of the report's Section 10 first.

One candidate explored in depth is worth more than several sketched. If no candidate meets the bar
(Section 3), say so, and say what came closest and why it falls short.

## 2. Finding candidates

Collect many ideas before judging any of them: most first ideas are incremental, and the good
ones often come from an unexpected angle, so a short list usually means that some angles were not
tried. With sub-agents, give each angle below to its own agent, with the inventory, the report and
the Lean project, and pool what they return.

- Questions others have asked. The paper's open questions and conjectures (Phase 1), those of
  the work it builds on, and those of the later work (Section 10 of the report), problem lists,
  MathOverflow. A question that someone posed in print is the best evidence that an answer is
  wanted.
- The method's limits. The hypotheses that the paper says it needs only for its method, and
  the natural stronger statement. Find the step where the paper's argument stops working for it:
  state the stronger statement in a scratch Lean file outside the library, follow the paper's
  proof, and see which lemma fails first. That lemma, stated exactly, is the obstacle, and an idea
  that removes it is a paper.
- Sharpness. Is the result optimal? A matching bound, a construction or a counterexample that
  shows a hypothesis is needed, or the exact threshold. Search small cases by computer
  (`references/numerics.md`, Section 1, for the tools).
- Transfer. The method in a neighbouring setting where the question is open and has its own
  readers: another class of objects, a quantitative, algorithmic or probabilistic version, another
  field or characteristic.
- The machinery. Something the proof builds that is more general than its use here, such as a
  new inequality, a construction or a certificate, and the other problems it would apply to.
- Connections. The paper's objects under another name in another area, and what is known
  there.
- The proof assistant as a tool. A certified computation that settles a case that matters (a
  counterexample, a finite check, an explicit constant) can be a paper in its own right. A paper
  about the formalization itself (for a venue such as ITP or CPP) belongs here only when the work
  needed a technique that others could reuse. Say so in a line; do not develop it.

## 3. The bar: a paper, not a remark

These are incremental. Record them in the report's Section 11, not in the follow-up file:

- a hypothesis that the proofs never use (it is already a finding of the audit);
- a variant that the same proof covers with routine changes;
- a better constant from the same argument, run more carefully;
- a corollary, or a more general setting in which nothing new happens;
- a simpler proof that saves a page or a citation.

A candidate is substantial when it does at least one of these:

- answers a question that someone has posed in print;
- needs a new idea: the paper's method fails at a step you can name, and the candidate says what
  could replace it;
- settles optimality: a matching bound, a counterexample to the natural extension, an exact
  threshold;
- opens a setting where the question was open and that has its own readers;
- gives a new proof that does more than the old one: it removes heavy machinery from a well-known
  result, or it generalizes where the old proof cannot.

Then test it. Write the abstract of the paper the candidate would become, as short as a journal
abstract. If its main theorem reads as "we observe that the proof of [the paper] also gives", it is
incremental.
Ask whether a journal of the paper's standing would take it, and whether the paper's authors would
find it a real step. A famous open problem is not a candidate by itself: name the partial result
that a paper could reach, and make that the target.

## 4. Exploring a candidate

Screen the raw ideas by the bar and by the literature, and keep the few with the best balance of
significance and feasibility. Explore each well beyond its description: give it the effort a
researcher would give to deciding whether to start a project, which is hours of work, not a
paragraph.

1. The target. State the theorem to aim for, with its quantifiers and hypotheses, and a weaker
   fallback that would still be a paper.
2. Novelty. Search for the target itself, not only for the paper's topic: arXiv full text,
   the papers that cite the paper and those it cites, MathOverflow, problem lists. Record the
   queries and the date. A candidate that turns out to be known leaves the follow-up file
   (Section 5). If the found work bears on the paper's results, tell the user.
3. Where the paper's method stops. Run the paper's proof against the target, and find the
   first step that fails and why: a counterexample to the step, or the estimate that loses. A
   scratch Lean file that states the target and follows the paper's proof shows the failing goal
   exactly. If no step fails, the candidate is a routine extension (Section 3).
4. Getting past it. Make at least one serious attempt: a technique from a connected area, a
   reduction to a cleaner statement, a special case. Record what was tried, what worked in part,
   and what failed and why. A special case proved, or a reduction to a clean statement, is often
   the most useful part of the file.
5. Evidence. Compute small cases, search for counterexamples, check the boundary and
   degenerate cases. Keep the scripts in `notes/follow-up/`, and record what was checked and how
   far.
6. What is proved. Prove each partial result carefully on paper. Check it in Lean when that is
   cheap, in a scratch file in `notes/follow-up/`, never in the library: the library is the
   paper's formalization, and these results are unpublished.
7. Assessment. What is proved, what is evidence and what is hope; the main risk; a first
   milestone, a lemma whose proof would show that the approach works; and the scale: a short note,
   a full paper or a longer programme.

Do not oversell. Mark each claim as proved (in Lean, or on paper), checked numerically (how far),
or conjectured. A plan whose key step is "prove the conjecture" is not a plan: say what new idea
the key step needs, or say that you do not have one.

## 5. Checking

Check each candidate independently of its writer (SKILL.md, Principles), and give the checker the
inventory, the report and the follow-up file:

- Novelty. Repeat the search independently and try to find the target in the literature.
- The bar. Read the draft abstract as a referee would, and decide whether the candidate is an
  incremental result in disguise.
- Claims. Work through every proof marked as proved, recompute every number by script, and
  rerun the evidence.
- The obstacle. Decide whether the paper's method really fails at the named step, or whether a
  routine change gets past it.

A candidate that turns out to be known moves to the report's Section 10, under "Before the paper",
"Concurrent work" or "Since the paper" as its source's date decides, and one that turns out to be
incremental moves to Section 11, "Open directions". Correct a wrong claim, or mark it as
conjectured.

## 6. Structure of the follow-up file

```markdown
# Follow-up papers to <authors>, *<title>*

Private: not published with the formalization. Written <date>; literature searched <date>.

## Summary
<One short paragraph per candidate, ranked: the target in a sentence, why it matters, what is
proved and what evidence there is, the main obstacle, and a recommendation. If no candidate meets
the bar, say so, and what came closest.>

## 1. <The title of the paper it would be>
### Target
<The theorem, with its hypotheses; the fallback.>
### Why it matters
<Who asked, what it would settle, who would read it; with links.>
### Novelty
<The searches and their date; the closest work, and how the target differs from it.>
### Where the paper's method stops
<The step, why it fails; the failing Lean goal, if found.>
### Ideas to get past it
<What was tried, what worked in part, what failed and why.>
### What was done here
<Each result proved, on paper or in Lean, and each computation, with its files in
`notes/follow-up/`.>
### Risks and first milestone
### Scale
<A note, a paper or a programme, and where it might appear.>
### Draft abstract

## 2. …

## Considered and set aside
<Every other idea, one line each, with why: incremental (now in the report's Section 11), known
(Section 10), or out of reach (what it lacks).>
```

## 7. Keeping it private

The follow-up file holds unpublished research ideas, and the formalization is usually published.
It and its scratch files stay in `notes/`, which git ignores (`lean-project.md`, Section 1). Before
writing it, check that git ignores it (`git check-ignore notes/follow-up-papers.md`). Never commit
it, and leave it out of every package and pull request. Publish it only if the user asks.

No public file of the project, `.gitignore` and `formalization.yaml` included, mentions the
follow-up file or says that a private file holds plans for follow-up papers. The report's "Open
directions" may name a question that the follow-up file develops, as it would without it, but not
the attack, the evidence or the partial results recorded there.

An ignored file is in no backup that the repository provides. When you finish, tell the user where
the follow-up file and `notes/follow-up/` are, and give them the summary in the status report.
