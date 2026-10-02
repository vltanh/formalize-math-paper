# Rigorous numerics in Lean

Papers often rest on numbers: a constant enclosed to a few digits, an inequality checked "by
computer", a system of equations "solved numerically", a figure that shows a curve stays on one
side of another. Each of these is a claim to prove. This guide collects methods that work without
`native_decide` (Comparator rejects the axiom it adds) and without trusting floating point.

## Contents

1. Plan in Python first
2. Interval arithmetic with `norm_num`
3. Elementary functions
4. Generated proofs
5. Integrals in closed form
6. Existence and uniqueness of a solution
7. Inequalities over two or more parameters
8. Zeros and tangencies

## 1. Plan in Python first

Before writing Lean, compute everything in Python (`mpmath` at high precision, `sympy` for exact
algebra, `numpy` and `scipy` for exploration):

- the values and their margins: how far each inequality is from failing, and where;
- the derivatives' signs on each interval, which decide where monotonicity arguments work;
- the points where an inequality becomes tight (a zero, or a tangency) and its order there.

The margins decide the method. A margin of 10⁻² needs crude bounds; a margin of 10⁻⁶, or a
tangency, needs an argument first (Sections 7 and 8), not a finer grid. Keep the scripts with the
project's notes, and give an agent the numbers together with the task.

## 2. Interval arithmetic with `norm_num`

Write each quantity as `x ∈ Set.Icc lo hi` with rational (or decimal) endpoints, and propagate
enclosures through small lemmas, one per operation:

```lean
lemma iv_add {x y a b c d : ℝ} (hx : x ∈ Icc a b) (hy : y ∈ Icc c d) : x + y ∈ Icc (a + c) (b + d) :=
  ⟨add_le_add hx.1 hy.1, add_le_add hx.2 hy.2⟩
```

Multiplication needs the four corner products. Prove one lemma `iv_mul` that takes the enclosure
of the product as hypotheses checked by `norm_num` (`L ≤ a*c ∧ L ≤ a*d ∧ …`), so that each use is a
single `norm_num` call on explicit rationals. Keep every step explicit; avoid one large `nlinarith`
over many enclosures, which is slow and fragile. Start from the enclosures the paper's parameters
satisfy, proved once (for parameters defined implicitly, by Section 6), and bundle them in a
structure so that hypotheses stay short.

## 3. Elementary functions

- π: Mathlib has decimal bounds (grep `pi_gt_d` and `pi_lt_d` in
  `Mathlib/Analysis/Real/Pi/Bounds.lean`).
- sin and cos: `Real.sin_bound` and `Real.cos_bound` (in
  `Mathlib/Analysis/Complex/Trigonometric.lean`) hold only for `|x| ≤ 1`, with errors `|x|^5/100`
  and `5|x|^4/96`. Higher-order alternating bounds, such as
  `sin x ≤ x - x^3/6 + x^5/120` and `1 - x^2/2 + x^4/24 - x^6/720 ≤ cos x` for `x ≥ 0`, follow by
  integrating a known bound several times, or from the monotonicity of the difference. Prove them
  once and reuse them. For larger arguments, reduce with `sin (π/2 - x) = cos x` and the like.
- exp and log: `Real.exp_bound` and `Real.add_one_le_exp` (in
  `Mathlib/Analysis/Complex/Exponential.lean`) give enclosures of `exp`;
  `Real.log_le_sub_one_of_pos` and monotonicity give those of `log`.
- Check every name with `#check` before relying on it: these lemmas are renamed often.

## 4. Generated proofs

Hundreds of interval steps are best generated. Write a Python generator that emits the Lean steps
(exact rationals with `fractions.Fraction`, derivatives and antiderivatives with `sympy`, each
inequality checked by `norm_num`), and:

- commit the generator with the project, and check that it reproduces the committed Lean file
  byte for byte;
- say in the README how to run it;
- keep each generated file under Palomar's 10,000-line limit, split into modules if needed;
- name template fragments that the generator assembles `*.lean.in`, because every `.lean` file
  must be a module.

## 5. Integrals in closed form

When an area or another integral has an elementary antiderivative, obtain it from `sympy`, prove
`HasDerivAt F f t` with the `HasDerivAt` combinators followed by `ring`, apply
`intervalIntegral.integral_eq_sub_of_hasDerivAt`, and evaluate `F b - F a` by interval
arithmetic. A function given piecewise is integrated piece by piece. One generic structure, such
as "polynomial coefficients times `1`, `cos t`, `sin t`" together with a lemma computing its
integral, covers many pieces at once.

## 6. Existence and uniqueness of a solution

To show that a system `H(z) = 0` has exactly one solution in a box `B` (for example the parameters
of an explicit construction that a paper takes from a numerical solution):

1. Eliminate the unknowns that enter linearly, symbolically, until few remain.
2. Choose a matrix `M` close to the inverse of the derivative `DH` at the approximate solution, and
   consider `G(z) = z - M·H(z)`.
3. Bound the entries of `I - M·DH(z)` on `B` by interval arithmetic (Section 2). A sum of
   absolute values per row below `q < 1` makes `G` a contraction for the sup norm.
4. Show that `G` maps a small box around the approximate solution into itself. Banach's theorem
   (`ContractingWith.exists_fixedPoint'`) then gives a zero there, and the contraction on all of
   `B` gives that it is the only zero in `B`.
5. Derive enclosures of every parameter from the small box. Later numerical lemmas assume these
   enclosures.

## 7. Inequalities over two or more parameters

A family of inequalities `F(s, τ) ≥ 0` over a rectangle (a point on one curve against a line
through another, for every pair of parameters) is expensive by brute force, and fails outright
where `F` vanishes. Reduce the dimension first:

- **Monotonicity in one variable.** If `∂F/∂τ` has a sign, or changes sign at most once (for
  example because it is the sign of `g(τ) - h(s - τ)` with `g` increasing and `h` decreasing), then
  `F` is monotone or unimodal in `τ`. So `F(s, τ) ≥ min(F(s, a), F(s, b))`, and only the edges
  remain: one-variable inequalities.
- **Convexity and envelopes.** For a family of lines, or of half-planes, with a smooth envelope,
  each line is tangent to the envelope, and a convex envelope lies on one side of all its tangent
  lines. Points of the envelope then satisfy the inequality for the whole range of parameters
  where the envelope is convex, with no computation.
- **Witness directions.** To show that a point is outside an intersection of half-planes, it is
  enough to find one direction that separates it. A covering argument can often choose that
  direction as a fixed parameter value for a whole region, which turns a two-parameter claim into
  a one-parameter one.
- **Algebraic identities.** Writing the quantity as an integral of a signed density, as with
  `F(τ) = ∫ ρ(r) sin(r - s) dr`, makes its sign visible on whole intervals.

Explore numerically (Section 1) to see which variable is monotone where, then write the reduction
as a short mathematical plan before the Lean.

## 8. Zeros and tangencies

An inequality `f ≥ 0` that is tight somewhere cannot be proved by enclosures near that point.

- **A simple zero at an endpoint** (`f(a) = 0 < f'(a)`): bound `f(x)/(x - a)` instead, after
  dividing out the factor symbolically, or show `f' > 0` on `[a, a + δ]` and use enclosures
  beyond.
- **A tangency** (`f(c) = f'(c) = 0` inside the interval): find the reason for it, which is usually
  an identity of the construction (two curves meeting at a point, a line tangent to its envelope).
  Prove that identity exactly, and use a second-order argument (convexity, or the sign of `f''`)
  near `c`.
- **A margin that is tiny but positive:** prove it at its own scale, with a reduction that
  isolates the small quantity. Do not try to refine a global grid until it passes.
