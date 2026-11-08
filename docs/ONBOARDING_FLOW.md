# LifeOS Onboarding Flow

## 1. Overview & Purpose

The LifeOS Onboarding experience guides newly registered users through personalizing their AI Personal Operating System immediately following account creation.

---

## 2. Step Breakdown

### Step 1: Welcome & Mission
- **Visual**: Glass hero badge with sparkle icon.
- **Content**: Welcomes user by first name (`user.full_name.split(' ')[0]`). Explains that LifeOS is a unified workspace for tasks, habits, schedules, goals, and finances powered by private local AI.
- **Security Callout**: Highlights local-first privacy and that data stays under the user's control.

### Step 2: Core Focus Areas (Pillars)
- **Component**: 2-column interactive glass choice cards with icon and label.
- **Options**:
  - `health`: Health & Fitness
  - `career`: Career & Ambition
  - `finance`: Financial Freedom
  - `knowledge`: Deep Knowledge
  - `productivity`: Daily Organization
  - `mindfulness`: Mental Clarity
- **Behavior**: Multi-select toggle. Default selection pre-selects `productivity` and `health`.

### Step 3: Initial Personal Goals
- **Component**: Glass list items with custom toggle checkboxes.
- **Options**:
  - `routine`: Establish a morning & evening routine
  - `deep_work`: Execute 4 hours of distraction-free deep work
  - `budget`: Track daily personal & business expenses
  - `workout`: Exercise 4 times per week consistently
  - `reading`: Read 20 pages of non-fiction daily
  - `meditate`: Practice 10 minutes of daily mindfulness

### Step 4: Preferences Configuration
- **AI Communication Style**:
  - `concise`: Short, bulleted answers.
  - `balanced`: Default balanced mode with brief context.
  - `comprehensive`: Detailed breakdowns, step-by-step guidance.
- **Notification Cadence**:
  - `daily_summary`: One morning/evening brief.
  - `realtime`: Instant updates on upcoming blocks and alerts.
  - `quiet`: No proactive notifications.

### Step 5: Summary & Activation
- **Visual**: Rocket icon in floating glass container.
- **Content**: Summary card showing total focus areas chosen, active targets count, and AI mode.
- **Action**: "Enter LifeOS" button invokes `completeOnboarding()`.

---

## 3. Persistence & Current Limitations

> [!IMPORTANT]
> **Persistence Limitation Notice**:
> At this development phase (STEP 06), backend endpoints for user preferences (`/api/v1/users/preferences`) and goal seeding have not yet been implemented on the Flask server.
>
> Therefore, onboarding choices are:
> 1. Persisted locally in `SecureStore` under keys `lifeos_onboarding_completed` and `lifeos_onboarding_prefs`.
> 2. Maintained in the Zustand `useAuthStore` session state (`hasCompletedOnboarding: boolean`, `onboardingPreferences: OnboardingPreferences`).
> 3. Marked with transparent UI indicators so the user understands these are local settings awaiting synchronization in upcoming Core Engine milestones.
>
> Onboarding data is NOT falsely reported as synchronized with the backend database until the respective backend preference endpoints are delivered in future steps.

