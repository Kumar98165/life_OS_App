# LifeOS Life Analytics API Reference

Base URL: `/api/v1/analytics`  
Authentication: Bearer JWT (`Authorization: Bearer <token>`)

---

## Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/overview` | Multi-domain summary payload (Life Score, Productivity, Habits, Goals, Finance) |
| `GET` | `/productivity` | Task completion rates, overdue counts, planner blocks, and daily velocity trend |
| `GET` | `/habits` | Habit consistency %, active habits, streaks, and check-in history |
| `GET` | `/goals` | Goal velocity, milestone completion %, and upcoming deadlines |
| `GET` | `/finance` | Income, expenses, net savings, savings rate %, and category distribution |
| `GET` | `/trends` | Multi-domain daily completion activity series |
| `GET` | `/life-score` | Transparent 0-100 composite score with dimension breakdown |
| `GET` | `/insights` | AI narrative synthesis with local Ollama or deterministic fallback |

---

## Query Parameters

Endpoints accepting date filtering support:
- `period`: `day` | `week` | `month` | `year` | `custom` (Default: `week`)
- `start_date`: `YYYY-MM-DD` (Required when `period=custom`)
- `end_date`: `YYYY-MM-DD` (Required when `period=custom`)
- `timezone`: Timezone name (e.g. `America/New_York`, Default: user preference or `UTC`)

---

## Sample Responses

### 1. `GET /api/v1/analytics/life-score`

```json
{
  "success": true,
  "message": "Life score calculated successfully",
  "data": {
    "overall_score": 85,
    "score_tier": "Exceptional",
    "period": "week",
    "dimensions": [
      {
        "name": "Productivity",
        "score": 88.0,
        "weight": 30.0,
        "weighted_score": 26.4,
        "description": "Tasks completion (85.0%) and Planner adherence (95.0%).",
        "status": "excellent"
      },
      {
        "name": "Habits",
        "score": 92.5,
        "weight": 30.0,
        "weighted_score": 27.8,
        "description": "Habit consistency (92.5%) across 4 active habits.",
        "status": "excellent"
      },
      {
        "name": "Goals",
        "score": 75.0,
        "weight": 20.0,
        "weighted_score": 15.0,
        "description": "Goal completion (50.0%) and Milestones (100.0%).",
        "status": "good"
      },
      {
        "name": "Financial Discipline",
        "score": 79.0,
        "weight": 20.0,
        "weighted_score": 15.8,
        "description": "Savings rate (60.0%) and Budget adherence (98.0%).",
        "status": "good"
      }
    ],
    "calculation_explanation": "Your Life Score of 85/100 represents a weighted composite...",
    "disclaimer": "This score is a personal productivity metric and is not a clinical, psychological, or medical assessment."
  }
}
```

### 2. `GET /api/v1/analytics/insights`

```json
{
  "success": true,
  "message": "AI personal insights generated successfully",
  "data": {
    "generated_at": "2026-11-08T14:40:00Z",
    "period": "week",
    "life_score": 85,
    "executive_summary": "You demonstrated high execution velocity with 88% task completion and sustained habit routines.",
    "productivity_observation": "Focus blocks scheduled in the morning achieved higher execution rates.",
    "habit_observation": "Daily morning routines are unbroken across your 4 active habits.",
    "financial_observation": "Net savings totaled $1,800 resulting in a 60% savings rate.",
    "actionable_recommendations": [
      "Protect your 9 AM deep work planner blocks.",
      "Complete evening habit check-ins before 10 PM.",
      "Review subscription categories to maintain targeted savings."
    ],
    "is_fallback": false
  }
}
```

