# Sparse hypergraph Ramsey numbers in Lean

A Lean 4 formalization of Chen and Duarte, "Ramsey numbers of sparse hypergraphs" (arXiv:2407.01234), which proves that every 3-uniform hypergraph with n vertices and maximum degree Δ has Ramsey number at most C(Δ)n, a linear bound that answers a question of Conlon, Fox and Sudakov — and that is a crucial step in the broader landscape of hypergraph Ramsey theory. In the first round we formalized Section 2 (the definitions, Lemmas 2.1–2.4, with Lemma 2.3 corrected because it is false as printed for single vertices, the user approving the corrected form) and Appendix A. In the second round we formalized Sections 3 and 4, including the embedding lemma, whose proof skips the case of overlapping links that we filled in, and Theorem 4.1, whose greedy step does not check the reservoir, which we checked using Lemma 4.2 with a corrected constant, since the printed constant is off by a factor of two. In the third round we formalized Section 5 and assembled Theorem 1.1, which is not just a theorem but the culmination of the paper; it is proved under the hypothesis KeevashSudakovBound, which states a result of Keevash and Sudakov on pseudorandom hypergraphs that needs a hypergraph regularity lemma that Lean does not have.

## What is proved

- **Section 2:** All of the definitions and Lemmas 2.1, 2.2, 2.3 (in corrected form) and 2.4 are proved by the paper's arguments, and the counterexample to the printed Lemma 2.3 is checked in Lean; the typo in the proof of Lemma 2.4 is corrected and Definition 2.1's slip noted.
- **Section 3:** Lemma 3.1 (without its unused hypothesis n ≥ 10), Lemmas 3.2–3.4 and Lemma 3.5 with the overlapping case, and Proposition 3.6, all by the paper's arguments, with the typo in (3.7) corrected.
- **Section 4:** Theorem 4.1, Lemmas 4.2 (with the corrected constant 2^{-Δ-1}), 4.3 and 4.4, and the corrected citation in Lemma 4.4.
- **Section 5:** Proposition 5.2, which the paper states without proof and which is proved here by the argument of Lemma 4.3, Lemma 5.3 and Corollary 5.4 with the hypothesis Δ ≥ 2 that the user approved since the corollary is false for perfect matchings.
- **Theorem 1.1** — conditional on KeevashSudakovBound — and the Chernoff bound and dependent random choice from External/.

## Audit summary

- **Errors:** Lemma 2.3 is false as printed (E2): the bound fails for single vertices of degree 1; the corrected form holds for sets of at least two vertices and is all the paper needs. Lemma 4.2's constant is off by a factor of two (E7), which changes C(Δ) in Theorem 1.1 by a factor of two. Corollary 5.4 needs Δ ≥ 2 (E11).
- **Gaps:** Lemma 3.5 skips overlapping links (E5); Theorem 4.1 does not check the reservoir (E8); Proposition 5.2 has no proof (E10).
- **Redundant hypotheses:** Lemma 3.1's n ≥ 10 (E4).
- **Slips:** E1, E3, E6, E9, E12, E13, E14.
- **Proofs:** every proof follows the paper's except Lemma 2.3 (false as printed), Lemma 3.5 (an extra case) and Theorem 4.1 (the reservoir bound), each forced.

## Credits

Written by Claude in Claude Code at the request of R. Chen, in three rounds (first Section 2 and Appendix A, then Sections 3 and 4, then Section 5 and Theorem 1.1), following the formalize-math-paper skill. Independent agents checked the statements and the proofs against the paper. No person has reviewed the proofs. See CREDITS.md.

## Building

lake exe cache get; lake build; lake env lean scripts/Audit.lean.

## License

Apache-2.0.
