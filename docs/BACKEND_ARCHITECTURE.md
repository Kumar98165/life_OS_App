# LifeOS – Backend Architecture

## 1. Overview
The LifeOS backend is designed as a modular **Python 3.13 Flask** service implementing **Clean Architecture** principles. It delivers strict separation between the transport layer (Blueprints/HTTP), validation layer (Pydantic), business logic (Services), and persistence layer (Repositories & SQLAlchemy).

Companion References:
- **[API_STANDARDS.md](file:///c:/Users/NexviTech/Desktop/LifePs/docs/API_STANDARDS.md)**: HTTP envelope standards, status codes, and headers.
- **[SECURITY_GUIDELINES.md](file:///c:/Users/NexviTech/Desktop/LifePs/docs/SECURITY_GUIDELINES.md)**: Cryptographic token revocation, resource ownership checks, and rate limiting.
- **[ERROR_HANDLING.md](file:///c:/Users/NexviTech/Desktop/LifePs/docs/ERROR_HANDLING.md)**: Centralized exception handling and error code taxonomy.
- **[TESTING_STRATEGY.md](file:///c:/Users/NexviTech/Desktop/LifePs/docs/TESTING_STRATEGY.md)**: Automated test suite, isolation, and coverage benchmarks.
- **[openapi.yaml](file:///c:/Users/NexviTech/Desktop/LifePs/docs/openapi.yaml)**: OpenAPI 3.1.0 interactive contract specification.

## 2. Directory Architecture (`backend/app`)
```
backend/
├── app/
│   ├── __init__.py           # Flask Application Factory (create_app)
│   ├── config.py             # Config classes (Base, Development, Testing, Production)
│   ├── extensions.py         # Extension singletons (db, migrate, jwt, cors, limiter)
│   ├── api/                  # Global API route aggregator
│   ├── blueprints/           # Modular HTTP controllers
│   │   ├── auth/             # Authentication & token endpoints
│   │   ├── users/            # User profile & preferences
│   │   ├── dashboard/        # Daily aggregation & productivity scores
│   │   ├── tasks/            # Task management & priority matrix
│   │   ├── planner/          # Time-block scheduling
│   │   ├── goals/            # Long-term goals & milestone tracking
│   │   ├── habits/           # Habit tracking & streaks
│   │   ├── ai/               # AI Chat & LangGraph agent endpoints
│   │   ├── memory/           # AI long-term context memory management
│   │   ├── finance/          # Budgets, accounts, and transactions
│   │   ├── notifications/    # Push notifications & reminder rules
│   │   └── health/           # Liveness (/health) and Readiness (/ready) probes
│   ├── core/                 # Cross-cutting foundational modules
│   │   ├── exceptions.py     # Typed domain exceptions (LifeOSException, etc.)
│   │   ├── handlers.py       # Centralized error interceptors
│   │   ├── response.py       # RFC-standard response serializers
│   │   ├── security.py       # Token revocation blocklist & ownership checks
│   │   ├── pagination.py     # Safe query pagination helper
│   │   └── logging.py        # Structured request tracing & timing
│   ├── models/               # SQLAlchemy 2.0 declarative database entities
│   ├── schemas/              # Pydantic input and output validation schemas
│   ├── repositories/         # Query encapsulation and database operations
│   └── services/             # Business workflows, transactional boundaries
├── migrations/               # Alembic database migration scripts
├── tests/                    # Pytest automated test suites (21 tests, 93% coverage)
├── requirements.txt          # Production and development dependencies
├── pytest.ini                # Pytest runtime configuration
├── run.py                    # Application runner
└── .env.example              # Environment variables template
```

## 3. Core Enterprise API Foundation

### 3.1 Request Tracing & Structured Logging
- Each request is tagged with an `X-Request-ID` header.
- Duration is measured in milliseconds.
- Sensitive information (passwords, JWT tokens, secrets) is strictly omitted from logging output.

### 3.2 Security & Ownership Boundaries
- Resource operations enforce `check_resource_ownership(resource.user_id, current_user_id)`.
- Client-provided `user_id` fields are never trusted for authorization.
- Token revocation is maintained via persistent JTI tracking in the `refresh_tokens` table.

### 3.3 Safe Query Pagination
- Reusable `paginate_query(query, page, per_page, max_per_page=100)` prevents excessive memory consumption.
