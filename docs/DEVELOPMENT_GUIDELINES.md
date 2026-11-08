# LifeOS – Development Guidelines

## 1. Engineering Philosophy
LifeOS is built to commercial-grade software engineering standards. Code must be readable, maintainable, performant, and secure.

## 2. Frontend Coding Standards (React Native & TypeScript)
1. **Strict TypeScript**:
   - Never use `any`. Always declare precise types, interfaces, or generics.
   - Domain models are placed in `@/types` or local feature `types.ts`.
2. **Component Separation**:
   - Keep UI components dumb and focused on layout and rendering.
   - Extract business logic, queries, and mutations into custom feature hooks (e.g., `useTasks`, `useAuth`).
3. **Performance First**:
   - Use `FlatList` with `keyExtractor` and memoized `renderItem` for lists.
   - Avoid re-creating objects or arrow functions within JSX renders.
4. **Design System Integrity**:
   - Never hardcode raw hex colors or arbitrary margin/padding values.
   - Always import design tokens from `@/theme` (`colors`, `spacing`, `borderRadius`, `shadows`).
5. **No Direct Network Calls**:
   - Components must never invoke Axios or `fetch` directly. All API operations go through TanStack Query hooks and service wrappers.

## 3. Backend Coding Standards (Python 3.13 & Flask)
1. **Layer Discipline**:
   - **Blueprints**: Request validation, status code assignment, response serialization. Zero SQL queries.
   - **Services**: Business rules, transactional control, authorization ownership checks.
   - **Repositories**: Pure SQLAlchemy query builders and database persistence.
2. **Input Validation**:
   - All inbound payloads must pass through Pydantic schemas.
   - Sanitize and normalize string values (e.g. email lowercasing) at schema parsing.
3. **Error Handling**:
   - Raise explicit domain exceptions (`NotFoundException`, `UnauthorizedException`, `ConflictException`, `ValidationException`).
   - Never catch and swallow exceptions silently.
   - Never return raw Python tracebacks to API clients.
4. **Database Integrity**:
   - Always wrap multi-entity mutations within explicit database transactions.
   - Avoid N+1 query patterns by using eager loading (`joinedload` / `selectinload`).

## 4. Security Protocols
1. **Secrets Management**:
   - Real passwords, database credentials, and secret keys must **never** be committed to Git.
   - `.env` files are ignored by `.gitignore`. Templates are committed via `.env.example`.
2. **Authorization & Ownership Checks**:
   - Always verify that the authenticated `user_id` matches the entity's owner before returning or mutating data.
3. **Password Security**:
   - Store passwords exclusively using salted `bcrypt` hashes with appropriate work factors (>= 12 rounds).
4. **JWT Lifespan**:
   - Access tokens have short lifespans (1 hour). Refresh tokens are long-lived (30 days) and revocable.

## 5. Testing & Verification Checklist
Before requesting approval for any development step:
1. Run frontend typecheck: `cd mobile && npx tsc --noEmit`.
2. Run backend test suite: `cd backend && .venv/Scripts/pytest -v`.
3. Verify database migrations run cleanly.
4. Ensure 0 regressions and 0 unhandled warnings.

