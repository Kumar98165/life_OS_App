# LifeOS – Planner Timezone & Date Strategy

## 1. Timezone Golden Rule

**"Store in UTC, Transmit in ISO 8601 with Offset, Display in User's Local Timezone."**

```
+-----------------------------------------------------------+
| Physical Device / Mobile Client                           |
|  - User selects: "09:00 AM" in their local timezone       |
|  - Client converts date + time to ISO: 2026-11-08T03:30:00Z|
+-----------------------------------------------------------+
                             |
                             v (JSON payload over HTTPS)
+-----------------------------------------------------------+
| Flask Backend                                             |
|  - Validates ISO string                                   |
|  - Normalizes to timezone-aware UTC datetime:             |
|    datetime(2026, 11, 8, 3, 30, 0, tzinfo=timezone.utc)   |
|  - Evaluates conflict detection in UTC                    |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
| PostgreSQL Persistence                                    |
|  - Stored in TIMESTAMP WITH TIME ZONE (TIMESTAMPTZ)       |
+-----------------------------------------------------------+
```

---

## 2. Calendar Day Window Computation

When querying for a specific local calendar day (e.g. `2026-11-08`), users expect events that occur between `00:00:00` and `23:59:59` **in their local timezone**, not UTC midnight.

### Backend Conversion Strategy
The mobile client passes its timezone offset in hours via `tz_offset`:
$$\text{local\_time} = \text{utc\_time} + \text{tz\_offset}$$
$$\text{utc\_start} = \text{local\_start} - \text{tz\_offset}$$
$$\text{utc\_end} = \text{local\_end} - \text{tz\_offset}$$

Example: User in India (+05:30):
- Local Day Start: `2026-11-08 00:00:00` $\rightarrow$ UTC Start: `2026-11-07 18:30:00Z`
- Local Day End: `2026-11-08 23:59:59` $\rightarrow$ UTC End: `2026-11-08 18:29:59Z`

Range queries using these boundaries return the exact items scheduled for the user's calendar day.

---

## 3. Daylight Saving Time (DST) & Midnight Crossing

- **Midnight Crossing**: A block starting at `23:00` and ending at `01:00` next morning is supported because `start_time` and `end_time` carry full ISO date-time timestamps.
- **DST Resiliency**: Because all records are stored as UTC timestamps, DST shifts (+/- 1 hour) do not distort the underlying duration of reserved blocks.
- **Strict Invariant**: `start_time < end_time` is enforced across all endpoints.

