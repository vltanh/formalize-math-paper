# Sharp thresholds for monotone 2-colorings in Lean 4

A Lean 4 formalization of B. Okafor and E. Lindqvist, *Sharp thresholds for monotone 2-colorings*
(arXiv:2603.04417).

## Main results

| Paper | Lean | Statement |
| --- | --- | --- |
| Theorem 1 | `Okafor.theorem1` | every monotone 2-coloring of `[n]²` has a monochromatic chain of length `n` |
| Theorem 3 | `Okafor.theorem3` | for `n ≥ 2`, the critical probability satisfies `p_c(n) ≤ 1/2 + 1/n` |
| Lemma 4 | not formalized | the coupling inequality of Section 4 |

## Status

| Section | Status |
| --- | --- |
| §2 | proved |
| §3 | proved |
| §4 | proved, except Lemma 4 |

## Building

`lake build`, then `lake env lean scripts/Audit.lean`.
