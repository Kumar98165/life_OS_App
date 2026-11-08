# LifeOS Streak Calculation Engine Algorithm

## 1. Streak Philosophy & Guarantees
1. **Never Break Early**: If today has not yet been logged, an active streak is **preserved** as long as the previous scheduled day was completed. The streak only resets to zero if yesterday (or the last scheduled day) was missed.
2. **Frequency-Aware Continuity**:
   - `daily`: Scheduled Monday through Sunday.
   - `weekdays`: Scheduled Monday through Friday. Saturday and Sunday are excluded from penalty and cannot break streaks.
   - `weekly`: Evaluated across calendar weeks (Monday to Sunday) based on `target_days_per_week`.
3. **No Unscheduled Logging**: Weekday-only habits cannot log on weekends, preventing artificial streak inflation.

---

## 2. Algorithms by Frequency

### A. Daily Streak Algorithm
Given set of completed dates $C \subseteq \text{Dates}$ and reference date $D_{ref} = \text{today}$:

```python
streak = 0
check_date = D_ref

if D_ref in C:
    streak += 1
    check_date = D_ref - 1 day
else:
    yesterday = D_ref - 1 day
    if yesterday in C:
        streak += 1
        check_date = yesterday - 1 day
    else:
        return 0

while check_date in C:
    streak += 1
    check_date = check_date - 1 day

return streak
```

### B. Weekdays-Only Streak Algorithm
Excludes weekends ($D.weekday() \ge 5$).

```python
if D_ref.is_weekday():
    if D_ref in C:
        streak += 1
        check_date = prev_scheduled_weekday(D_ref)
    else:
        prev_wkday = prev_scheduled_weekday(D_ref)
        if prev_wkday in C:
            streak += 1
            check_date = prev_scheduled_weekday(prev_wkday)
        else:
            return 0
else:
    # On weekend, last scheduled day was Friday
    last_friday = D_ref - (D_ref.weekday() - 4) days
    if last_friday in C:
        streak += 1
        check_date = prev_scheduled_weekday(last_friday)
    else:
        return 0

while check_date in C:
    streak += 1
    check_date = prev_scheduled_weekday(check_date)
```

Where `prev_scheduled_weekday(d)` returns $d - 3\text{ days}$ if $d$ is Monday, and $d - 1\text{ day}$ otherwise.

### C. Weekly Target Algorithm
1. Group completions by calendar week starting on Monday.
2. A week is marked **achieved** if $\text{count} \ge \text{target\_days\_per\_week}$.
3. For current week: if already achieved, streak increments. If current week is ongoing and not yet achieved, streak remains alive if the previous week was achieved.
4. Continue backwards through consecutive weeks.

---

## 3. Statistical Consistency Metrics
- **30-Day Consistency**:
  $$\text{Consistency}_{30} = \frac{\text{Completed days in last 30 days}}{\text{Scheduled days in last 30 days}} \times 100$$
- **7-Day Consistency**:
  $$\text{Consistency}_{7} = \frac{\text{Completed days in last 7 days}}{\text{Scheduled days in last 7 days}} \times 100$$
- **Total Completed Days**: Exact count of logs where `completed == True`.

