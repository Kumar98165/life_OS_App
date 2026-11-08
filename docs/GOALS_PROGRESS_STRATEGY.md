# LifeOS – Goal Progress Calculation Strategy

## 1. Mathematical Progress Invariant

The completion progress of a goal is calculated based on its concrete milestones:

$$\text{progress\_percent} = \frac{\sum_{i=1}^{N} \mathbb{I}(m_i.\text{is\_completed})}{N} \times 100$$

Where:
- $N$ is the total count of milestones belonging to the goal.
- $\mathbb{I}(\cdot)$ is the indicator function ($1$ if true, $0$ if false).

### Edge Cases
1. **Zero Milestones ($N = 0$)**:
   - If a goal has zero milestones, `progress_percent` is explicitly $0.0\%$.
   - This prevents division by zero (`ZeroDivisionError` / `NaN`).
2. **Rounding Precision**:
   - Progress percentages are rounded to 1 decimal place on the backend (e.g. $1/3 \rightarrow 33.3\%$) and formatted cleanly as integers on mobile UI cards ($33\%$).

---

## 2. Status Mutation Policy vs Progress

- **Goal Completion**: When a goal reaches $100\%$ progress (all milestones completed), the goal's status is **not** automatically forced to `'completed'` without explicit user intent. Users may have retrospective reviews or final sign-offs.
- **Manual Goal Completion**: If a user marks a goal as `'completed'` via the edit modal, its status transitions to `'completed'`.
- **Reopening Checkpoints**: If a user uncompletes a milestone on a $100\%$ goal, the progress drops accordingly (e.g. back to $75\%$).

---

## 3. Server-Authoritative Integrity

- Clients are never permitted to send an arbitrary `progress_percent` field in request payloads.
- Whenever a milestone is created, updated, toggled, or deleted:
  1. The database transaction executes the milestone operation.
  2. `goal_repo.recalculate_progress(goal_id)` counts active checkpoints in PostgreSQL.
  3. The parent goal's `progress_percent` is updated in the database.
  4. Both the modified milestone and the refreshed goal are returned to the client in the API response envelope.

