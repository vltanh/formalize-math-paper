# Rigorous numerics in Lean

Papers often rest on numbers: a constant bounded to a few digits, an inequality checked "by
computer", a system of equations "solved numerically", a figure that shows a curve stays on
one side of another. Each of these is a claim to prove. This guide collects methods that work
without `native_decide` (Comparator rejects the axioms it adds) and without trusting floating
point.

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
- the signs of the derivatives on each interval, which decide where monotonicity arguments work;
- the points where an inequality becomes tight (a zero, or a tangency), and its order there.

The margins decide the method. A margin of 10⁻² needs only crude bounds. A margin of 10⁻⁶, or a
tangency, needs an argument first (Sections 7 and 8), not a finer grid. Keep the scripts with the
project's notes, and give an agent the numbers together with the task.

## 2. Interval arithmetic with `norm_num`

Write each quantity as `x ∈ Set.Icc lo hi` with rational (or decimal) endpoints, and carry these
enclosures through small lemmas, one per operation:

```lean
open Set in
lemma iv_add {x y a b c d : ℝ} (hx : x ∈ Icc a b) (hy : y ∈ Icc c d) : x + y ∈ Icc (a + c) (b + d) :=
  ⟨add_le_add hx.1 hy.1, add_le_add hx.2 hy.2⟩
```

Multiplication needs the four corner products. Prove one lemma `iv_mul` that takes the enclosure
of the product as hypotheses checked by `norm_num` (`L ≤ a*c ∧ L ≤ a*d ∧ …`), so that each use is a
single `norm_num` call on explicit rationals. Keep every step explicit. Avoid one large `nlinarith`
over many enclosures: it is slow and fragile. Start from the enclosures the paper's parameters
satisfy, proved once (for parameters defined implicitly, by Section 6), and bundle them in a
structure so that hypotheses stay short.

## 3. Elementary functions

Mathlib has explicit bounds for π (decimal bounds such as `Real.pi_gt_d6`), sin and cos
(`Real.sin_bound`, `Real.cos_bound`, for `|x| ≤ 1`), exp (`Real.exp_bound`, `Real.add_one_le_exp`)
and log (`Real.log_le_sub_one_of_pos`). They hold on limited ranges, with crude errors. Reduce the
arguments by symmetries or functional equations. Derive once the sharper bounds that the problem
needs, and reuse them. Higher-order Taylor bounds follow by integrating a known bound, or from the
monotonicity of a difference. Check every name with `#check` before you rely on it: these lemmas
are renamed often.

## 4. Generated proofs

Hundreds of interval steps are best generated. Write a Python generator that prints the Lean steps
(exact rationals with `fractions.Fraction`, derivatives and antiderivatives with `sympy`, each
inequality checked by `norm_num`), and:

- commit the generator with the project, and check that it reproduces the committed Lean file
  byte for byte;
- say in the README how to run it;
- keep each generated file under Palomar's limit of 10,000 lines, split into modules if needed;
- name the template fragments that the generator assembles `*.lean.in`, because every `.lean` file
  must be a module.

## 5. Integrals in closed form

When an area or another integral has an elementary antiderivative, get it from `sympy`. Prove
`HasDerivAt F (f t) t` with the `HasDerivAt` combinators followed by `ring`, apply
`intervalIntegral.integral_eq_sub_of_hasDerivAt`, and evaluate `F b - F a` by interval
arithmetic. If a function is given piecewise, integrate it piece by piece. When many pieces share
one form (for example, polynomials times `cos t` and `sin t`, or times exponentials), one structure
for that form, with a lemma that computes its integral, covers them all at once.

## 6. Existence and uniqueness of a solution

To show that a system `H(z) = 0` has exactly one solution in a box `B` (for example, the parameters
of an explicit construction that a paper takes from a numerical solution):

1. Eliminate the unknowns that enter linearly, symbolically, until few remain.
2. Choose a matrix `M` close to the inverse of the derivative `DH` at the approximate solution, and
   consider `G(z) = z - M·H(z)`.
3. Bound the entries of `I - M·DH(z)` on `B` by interval arithmetic (Section 2). If the sum of
   absolute values in each row is below `q < 1`, then `G` is a contraction for the sup norm (`B`
   is convex, so the mean value inequality applies).
4. Check that `M` is invertible, for example by its determinant, an explicit rational. Then the
   fixed points of `G` are exactly the zeros of `H`.
5. Show that `G` maps a small box `B'` around the approximate solution `z₀` into itself. For the
   ball of radius `r` around `z₀` in the sup norm, inside `B`, it is enough that
   `‖M·H(z₀)‖ ≤ (1 - q)·r`.
   Banach's theorem (`ContractingWith.exists_fixedPoint'`) then gives a zero in `B'`, and the
   contraction on all of `B` makes it the only zero in `B`.
6. Derive enclosures of every parameter from `B'`. Later numerical lemmas assume these
   enclosures.

## 7. Inequalities over two or more parameters

Proving a family of inequalities `F(s, τ) ≥ 0` over a rectangle by brute force is expensive, and it
fails outright where `F` vanishes. Reduce the dimension first:

- **Monotonicity in one variable.** If `∂F/∂τ` has a sign, `F` is monotone in `τ`. If it is first
  `≥ 0` and then `≤ 0` (for example, because it has the sign of a function that decreases in `τ`,
  such as `h(s - τ) - g(τ)` with `g` and `h` increasing), `F` has no interior minimum in `τ`. In
  both cases `F(s, τ) ≥ min(F(s, a), F(s, b))`, and only the edges remain: inequalities in one
  variable. A change of sign from `-` to `+` gives an interior minimum, which needs its own
  argument.
- **Integral representations.** Where possible, write the quantity as an integral whose integrand
  has a known sign, as with `F(s) = ∫ ρ(r) sin(r - s) dr` with `ρ ≥ 0` over a range where
  `sin(r - s) ≥ 0`. This proves its sign on whole intervals at once.
- **The structure of the problem.** Convexity, or a covering of the parameter region by finitely
  many pieces with one witness on each, often turns a claim in two parameters into claims in
  one parameter.

Explore numerically (Section 1) to see which variable is monotone where. Then write the reduction
as a short mathematical plan before writing the Lean.

## 8. Zeros and tangencies

An inequality `f ≥ 0` that is tight somewhere cannot be proved by enclosures near that point.

- **A simple zero at an endpoint** (`f(a) = 0 < f'(a)`): bound `f(x)/(x - a)` instead, after
  dividing out the factor symbolically, or show `f' > 0` on `[a, a + δ]` and use enclosures
  beyond.
- **A tangency** (`f(c) = f'(c) = 0` inside the interval): find its cause, which is usually an
  identity of the construction. Prove that identity exactly, and use a second-order argument
  (convexity, or the sign of `f''`) near `c`.
- **A margin that is tiny but positive:** prove it at its own scale, with a reduction that
  isolates the small quantity. Do not try to refine a global grid until it passes.
