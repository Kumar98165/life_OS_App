# LifeOS – Project Architecture

## 1. Executive Summary & Vision
LifeOS is an intelligent, offline-first personal operating system designed to unify daily planning, task execution, habit building, long-term goal tracking, personal finance, knowledge notes, and context-aware local AI assistance. Built with a **Premium White Glassmorphism** interface, LifeOS prioritizes privacy, lightning-fast interactions, and zero-leakage local AI processing.

## 2. High-Level System Architecture

```
+--------------------------------------------------------------------------+
|                     LIFEOS MOBILE CLIENT (EXPO / RN)                     |
|                                                                          |
|  +--------------------+  +----------------------+  +------------------+  |
|  | Presentation Layer |  | State Management     |  | Service Layer    |  |
|  | - Glass Primitives |  | - TanStack Query v5  |  | - Axios Client   |  |
|  | - Feature Screens  |  | - Zustand Global     |  | - Auth Intercept |  |
|  | - React Navigation |  | - Secure Storage     |  | - Offline Sync   |  |
|  +--------------------+  +----------------------+  +------------------+  |
+--------------------------------------------------------------------------+
                                     |
                             REST / Bearer JWT
                                     v
+--------------------------------------------------------------------------+
|                     LIFEOS BACKEND API (FLASK MODULAR)                   |
|                                                                          |
|  +--------------------+  +----------------------+  +------------------+  |
|  | Routing / API BPs  |  | Business Services    |  | Data Layer       |  |
|  | - Auth, Tasks      |  | - Validation (Zod)   |  | - Repositories   |  |
|  | - Habits, Goals    |  | - Domain Exceptions  |  | - SQLAlchemy 2.0 |  |
|  | - Finance, AI BP   |  | - Transactions       |  | - Alembic Migr.  |  |
|  +--------------------+  +----------------------+  +------------------+  |
+--------------------------------------------------------------------------+
             |                                             |
             v                                             v
+------------------------+                    +----------------------------+
|   POSTGRESQL 18 RDBMS  |                    |     LOCAL OLLAMA RUNTIME   |
| - Users & Auth Tokens  |                    | - Qwen 2.5 (3B parameters) |
| - Tasks & Priority     |                    | - LangGraph Orchestration  |
| - Habits & Streaks     |                    | - LangChain Tool Engine    |
| - Finance & Analytics  |                    | - 100% On-Device Privacy   |
+------------------------+                    +----------------------------+
```

## 3. Core Monorepo Layout
```
LifePs/
├── backend/                  # Python 3.13 Flask REST API service
│   ├── app/                  # Application package (API, models, services)
│   ├── migrations/           # Alembic versioned migration scripts
│   ├── tests/                # Automated pytest test suites
│   ├── requirements.txt      # Pinned Python package dependencies
│   ├── run.py                # WSGI entry point
│   ├── pytest.ini            # Pytest configuration
│   └── .env.example          # Environment variable template
├── mobile/                   # React Native (Expo SDK 52+) TypeScript client
│   ├── assets/               # Static icons, splashes, and vectors
│   ├── src/                  # Source codebase
│   │   ├── api/              # Centralized Axios network client
│   │   ├── components/       # Reusable Glassmorphism UI primitives
│   │   ├── features/         # Feature-first slices (tasks, habits, etc.)
│   │   ├── hooks/            # Custom application hooks
│   │   ├── navigation/       # Navigation navigators & stacks
│   │   ├── screens/          # Screen views
│   │   ├── services/         # Client-side domain services
│   │   ├── store/            # Zustand global reactive stores
│   │   ├── theme/            # Design system tokens (colors, spacing)
│   │   ├── types/            # TypeScript domain interfaces
│   │   └── utils/            # Shared utilities and formatters
│   ├── package.json          # Node dependencies
│   ├── tsconfig.json         # TypeScript compiler configurations
│   └── .env.example          # Mobile environment configuration
├── docs/                     # Architectural and operational documentation
│   ├── PROJECT_ARCHITECTURE.md
│   ├── FRONTEND_ARCHITECTURE.md
│   ├── BACKEND_ARCHITECTURE.md
│   ├── DATABASE_ARCHITECTURE.md
│   └── DEVELOPMENT_GUIDELINES.md
└── .gitignore                # Global source control exclusion rules
```

## 4. Key Architectural Decisions
1. **Separation of Concerns**: UI rendering is decoupled from server caching (TanStack Query) and local state (Zustand). Backend HTTP routes only validate input and invoke business services; services delegate database operations to repositories.
2. **Local-First AI Integration**: AI capabilities operate on top of local Ollama models (`qwen2.5:3b`), ensuring user data never leaves the host machine.
3. **Consistent Error & Response Envelopes**: All API responses conform to `{ status: "success" | "error", message: string, data?: any, errors?: any }`.

