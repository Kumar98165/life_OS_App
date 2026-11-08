# LifeOS – Frontend Architecture

## 1. Overview
The LifeOS mobile client is built with **React Native**, **Expo SDK 52+**, and strict **TypeScript 5**. It adopts a **Feature-Based Architecture** paired with a **Premium White Glassmorphism** design system.

## 2. Directory Architecture (`mobile/src`)
```
mobile/src/
├── api/                     # Network layer: Axios instance, interceptors, error parsers
├── components/              # Shared UI design system primitives
│   ├── common/              # Text, Buttons, Badges, Dividers
│   ├── glass/               # GlassCard, GlassModal, GlassHeader
│   ├── feedback/            # Toast, Skeleton, Loaders, ErrorBoundary
│   └── layout/              # SafeScreen, Container, Spacer
├── features/                # Feature-based domain slices
│   ├── auth/                # Login, Register, Forgot Password
│   ├── dashboard/           # Daily summary score, quick action widgets
│   ├── planner/             # Day planner, timeline schedule, time-blocking
│   ├── tasks/               # Priority matrix, subtasks, task list
│   ├── goals/               # Long-term OKRs, milestones, progress bars
│   ├── habits/              # Streaks, heatmaps, daily completion trackers
│   ├── ai_assistant/        # Chat interface, streaming responses, tool cards
│   ├── ai_memory/           # Context memory viewer, facts inspector
│   ├── finance/             # Expense tracking, budget meters, categories
│   ├── analytics/           # Productivity metrics, habit correlation graphs
│   └── notifications/       # Local reminders, scheduled alerts, badges
├── hooks/                   # Custom reusable React hooks
├── navigation/              # React Navigation navigators (Auth, Tabs, Modals)
├── screens/                 # Screen controllers binding features to routes
├── services/                # Local storage, notification scheduling services
├── store/                   # Zustand stores (useAuthStore, useSettingsStore)
├── theme/                   # Colors, Typography, Spacing, Shadows
├── types/                   # Shared TypeScript contracts and entity models
└── utils/                   # Date formatters, math calculations, validators
```

## 3. Design System: Premium White Glassmorphism
The design system enforces high-contrast, clean-white visuals with frosted glass accents:
- **Background**: `#F7F8FC`
- **Primary Iris**: `#6C63FF`
- **Text Primary**: `#202033` (contrast ratio > 11:1)
- **Text Secondary**: `#85859A` (contrast ratio > 4.5:1)
- **Surface**: `#FFFFFF` with translucent overlays (`rgba(255, 255, 255, 0.75)`)
- **Border**: `#E9EAF2` / `rgba(255, 255, 255, 0.85)`
- **Feedback**:
  - Success: `#22C55E`
  - Warning: `#F59E0B`
  - Error: `#EF4444`

### Rules of Glassmorphism:
1. Glass effects must use hardware-accelerated shadows (`shadowColor: #1A1C35`, low opacity) and sub-pixel borders.
2. Readability is paramount: text is always rendered on opaque or high-opacity backgrounds (`>= 0.75`).
3. Heavy blur views are minimized inside high-frequency scroll lists to maintain 60 FPS.

## 4. State Management Strategy
1. **Server State (TanStack Query v5)**:
   - Queries handle asynchronous API caching, background refetching, and pagination.
   - Mutations use optimistic updates for instant UI responsiveness.
2. **Client State (Zustand v5)**:
   - Lightweight, un-opinionated stores for persistent auth session (`useAuthStore`) and user preferences (`useSettingsStore`).
3. **Form State (React Hook Form + Zod)**:
   - High-performance uncontrolled inputs with type-safe schema validation.

## 5. Performance Guidelines
- Use `FlatList` with `getItemLayout`, `keyExtractor`, and `windowSize={5}` for all dynamic collections.
- Avoid passing inline anonymous functions as props to list items.
- Memoize expensive calculations with `useMemo` and callbacks with `useCallback`.

