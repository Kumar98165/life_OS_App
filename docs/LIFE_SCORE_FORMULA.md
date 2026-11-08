# Life Score Formula & Weight Normalization Engine

## 1. Objective

The **Life Score** is a transparent, objective 0-100 composite index quantifying personal progress, consistency, and discipline across four core pillars:
1. **Productivity** (30% base weight)
2. **Habits** (30% base weight)
3. **Goals** (20% base weight)
4. **Financial Discipline** (20% base weight)

---

## 2. Pillar Calculation Formulas

### A. Productivity Pillar ($S_{\text{prod}}$)
Combines actionable task completion with planner block execution:
$$S_{\text{prod}} = (C_{\text{tasks}} \times 0.70) + (C_{\text{planner}} \times 0.30)$$
Where:
- $C_{\text{tasks}} = \frac{\text{completed\_tasks}}{\text{completed\_tasks} + \text{pending\_tasks}} \times 100$
- $C_{\text{planner}} = \frac{\text{completed\_blocks}}{\text{scheduled\_blocks}} \times 100$

### B. Habits Pillar ($S_{\text{habits}}$)
Reflects routine check-in consistency over scheduled check-in frequency (respecting daily, weekday, and weekly targets):
$$S_{\text{habits}} = \frac{\text{total\_completed\_checkins}}{\text{total\_scheduled\_checkins}} \times 100$$

### C. Goals Pillar ($S_{\text{goals}}$)
Balances long-term goal completion with near-term milestone velocity:
$$S_{\text{goals}} = (C_{\text{goals}} \times 0.50) + (C_{\text{milestones}} \times 0.50)$$
Where:
- $C_{\text{goals}} = \frac{\text{completed\_goals}}{\text{total\_active\_goals}} \times 100$
- $C_{\text{milestones}} = \frac{\text{completed\_milestones}}{\text{total\_milestones}} \times 100$

### D. Financial Discipline Pillar ($S_{\text{finance}}$)
Balances savings rate performance and monthly budget adherence:
$$S_{\text{finance}} = (R_{\text{savings}} \times 0.50) + (A_{\text{budget}} \times 0.50)$$
Where:
- $R_{\text{savings}} = \min(100, \text{savings\_rate} \times 2.0)$ (A 50% savings rate yields 100 points)
- $A_{\text{budget}} = \text{budget\_adherence\_percentage}$

---

## 3. Dynamic Weight Re-Normalization (Zero Penalization)

If a user has not logged data for a pillar (for instance, a user who tracks tasks and habits but has not entered finance or goals), penalizing them with 0 points would artificially distort their score. 

The Life Score Engine detects active domains and re-normalizes weights:

$$W_i' = \frac{W_i}{\sum_{j \in \text{active}} W_j}$$

$$\text{Overall Life Score} = \text{round}\left( \sum_{i \in \text{active}} S_i \times W_i' \right)$$

If no user data exists across all four pillars, the user is assigned a baseline score of 100 with status `unpenalized_no_data`.

---

## 4. Score Tiers

| Score Range | Score Tier | Classification |
|-------------|------------|----------------|
| 85 – 100 | **Exceptional** | Peak performance, sustained consistency, high adherence |
| 70 – 84 | **Strong** | Solid execution, steady routines with minor variance |
| 50 – 69 | **Balanced** | Moderate progress, baseline momentum |
| 0 – 49 | **Building Momentum** | Early stage, opportunities for focus and routine building |

---

## 5. Non-Medical Disclaimer

> [!NOTE]
> The Life Score is a personal productivity metric intended for self-reflection and habit tracking. It is **not** a clinical, psychological, psychiatric, or medical assessment.

