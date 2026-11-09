# LifeOS Advanced Personalization Architecture

## 1. System Overview

Step 21 introduces an enterprise-grade, privacy-centric personalization layer across the entire LifeOS platform. Rather than using opaque, black-box AI assumptions, LifeOS provides explicit, user-editable preferences that steer the AI Assistant, Daily Routine rhythm, and Mobile Dashboard layout.

```
 [User Configures Preferences]
              │
              ├── Personal Identity & Regional Formats (Preferred Name, Language, Date/Time, Week Start)
              ├── Productivity & Priority Strategies (Eisenhower, Deep Work, Pomodoro)
              ├── AI Assistant Tone & Length (Concise, Detailed, Motivational, Formal)
              ├── Daily Rhythm & Working Schedule (Sleep/Wake hours, Work window, Break intervals)
              └── Dashboard Layout (Custom widget ordering, Visibility toggles, Density)
              │
              ▼
   [PostgreSQL Database]
        ├── `user_personalizations`
        └── `daily_routines`
              │
              ▼
    [LifeOS Context Engine] ──> Real-Time Prompt Injection ──> [Local Ollama LLM / LangGraph]
              │
              ▼
   [Personalized Experience Across Tasks, Planner, Habits, Dashboard, and AI Assistant]
```

---

## 2. Core Pillars

1. **User Ownership & Explicit Consent**:
   - The system never silently infers or saves sensitive personal attributes.
   - All settings default to sensible, un-invasive values (`UTC`, `en`, `YYYY-MM-DD`, `24h`, `structured`).
   - Personalization can be enabled or disabled globally via a single toggle without wiping underlying data.

2. **Personalized AI Assistant**:
   - The AI Assistant reads the user's preferred name, desired tone, response length, and working hours directly from the Context Engine.
   - Daily planning suggestions adapt to the user's declared schedule (e.g., suggesting tasks during active work windows, avoiding sleep hours).

3. **Configurable Dashboard Architecture**:
   - Dashboard cards can be reordered up and down and toggled visible/hidden per user.
   - Layout density can be switched between `comfortable` (standard) and `compact`.
   - Layout state is persisted per user via `/api/v1/personalization/dashboard`.

4. **Daily Rhythm Integration**:
   - Stores typical wake, sleep, work start, work end, and planning times.
   - Connects directly into morning/evening ritual prompts and planner intervals without replacing the core scheduler.

5. **Granular Reset Capabilities**:
   - Provides targeted reset options (`dashboard`, `routine`, `identity`, `ai_style`, `all`) that restore defaults without deleting tasks, habit streaks, financial accounts, or confirmed AI memories.
