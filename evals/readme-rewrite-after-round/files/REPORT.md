# Audit of Chen and Duarte, "Ramsey numbers of sparse hypergraphs" (arXiv:2407.01234v2)

## Status

- Sections 2–5 and Appendix A of the paper are formalized. Every numbered result there is proved,
  three of them in corrected form (E2, E7, E11), by the paper's own arguments except where
  Section 7 lists a departure.
- **Conditional:** Theorem 1.1 (the main theorem: `r(H) ≤ C(Δ) n` for every `n`-vertex 3-uniform
  hypergraph `H` of maximum degree `Δ`) is proved under one named hypothesis,
  `KeevashSudakovBound`, which states Theorem 3 of Keevash and Sudakov (2019) on the edge
  distribution of pseudorandom hypergraphs. That theorem needs a hypergraph regularity lemma that
  no Lean library has; building it is a large effort, and the user chose to assume it for now.
  `theorem1_1` takes it as an explicit hypothesis; no axiom is used.
- Section 6 (applications to Ramsey goodness) is not formalized.
- `lake build` succeeds with no `sorry` outside `Challenge.lean`; every declaration depends only on
  `propext`, `Classical.choice` and `Quot.sound` (`scripts/Audit.lean`).
- The route check passes: 41 results, 23 differences, all recorded in `docs/route_differences.tsv`.
- Independent agents reviewed the statements against the TeX source and compared the proofs with the
  paper's. No person has reviewed the proofs.

## 1. Summary

Errors: Lemma 2.3 is false as printed (E2); the constant in Lemma 4.2 is off by a factor of 2 (E7);
Corollary 5.4 needs `Δ ≥ 2` (E11). Gaps: the embedding lemma (Lemma 3.5) skips the case of
overlapping links (E5); the greedy step of Theorem 4.1 does not check that the reservoir stays
large (E8); Proposition 5.2 is stated without proof (E10). Redundant hypotheses: Lemma 3.1 does not
need `n ≥ 10` (E4). Slips: E1, E3, E6, E9, E12, E13, E14.

## 2. Results from prior work

| Result | Source | Status |
| --- | --- | --- |
| Chernoff bound for hypergeometric distributions | Janson, Łuczak, Ruciński (2000) | proved in `External/` |
| Dependent random choice | Fox and Sudakov (2011), Lemma 2.1 | proved in `External/` |
| Edge distribution of pseudorandom hypergraphs | Keevash and Sudakov (2019), Theorem 3 | **assumed** as `KeevashSudakovBound` |

## 3. Errors and gaps

**E1. Definition 2.1 (TeX 210).** "`k`-uniform" is used before it is defined. Slip.

**E2. Lemma 2.3 (TeX 340–372): false as printed.** The bound `|N(S)| ≥ |S|Δ/2` fails for `S` a
single vertex of degree 1 (counterexample in Lean, `lemma2_3_counterexample`). It holds for `|S| ≥ 2`,
which is all the paper uses; the formalization states and proves that form (approved by the user).

**E3.** Typo in the proof of Lemma 2.4: `e(A, B)` for `e(B, A)`.

**E4. Lemma 3.1.** The hypothesis `n ≥ 10` is never used; the Lean statement omits it.

**E5. Lemma 3.5 (TeX 610–688): gap.** The embedding argument does not treat the case where two
links overlap. The case holds by the same counting, done in `lemma3_5_overlap`.

**E6.** Typo in (3.7): the sum runs to `t`, not `t - 1`.

**E7. Lemma 4.2 (TeX 801): wrong constant.** The bound `2^{-Δ}` should be `2^{-Δ-1}`; checked by
computation for `Δ = 3`. The corrected constant changes `C(Δ)` in Theorem 1.1 by a factor of 2.

**E8. Theorem 4.1 (TeX 830–902): gap.** The greedy step needs the reservoir to keep `n/4` vertices;
the paper does not check it. It holds by Lemma 4.2 with the corrected constant.

**E9.** Lemma 4.4 cites "Lemma 3.6" for Lemma 3.5.

**E10. Proposition 5.2: stated without proof.** Proved here by the argument of Lemma 4.3.

**E11. Corollary 5.4 (TeX 1102): missing hypothesis.** False for `Δ = 1` (a perfect matching);
proved with `Δ ≥ 2` (approved by the user).

**E12–E14.** Notation slips in Appendix A.

## 7. Departures from the paper's proofs

| Result | Paper | Formalization | Reason |
| --- | --- | --- | --- |
| Lemma 2.3 | the printed bound | the bound for `\|S\| ≥ 2` | false as printed (E2) |
| Lemma 3.5 | one case | two cases | gap (E5) |
| Theorem 4.1 | greedy embedding | the same, with the reservoir bound proved | gap (E8) |

## 9. Not formalized

Section 6 (Ramsey goodness), Remark 5.6 (a conjecture).

## 10. The paper in the literature

The bound improves Conlon, Fox and Sudakov (2009). Concurrent work of Lee (arXiv:2406.05555)
proves a weaker bound by different means. We found no earlier formalization of Ramsey numbers of
hypergraphs beyond Mathlib's graph Ramsey theory.

## 11. What's next

Proving `KeevashSudakovBound` needs a hypergraph regularity lemma for 3-uniform hypergraphs; the work
could be planned in layers. Section 6 depends only on Theorem 1.1.
