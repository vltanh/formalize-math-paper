module

public import Okafor.Section3

@[expose] public section

namespace Okafor

/-- **Theorem 3** (`thm:threshold`). For `n ≥ 2`, the critical probability of the monotone
2-coloring process on `[n]²` satisfies `criticalProb n ≤ 1/2 + 1/n`. -/
theorem theorem3 (n : ℕ) : criticalProb n ≤ 1 / 2 + 1 / (n : ℝ) :=
  criticalProb_le_of_coupling n (coupling_bound n)

end Okafor
