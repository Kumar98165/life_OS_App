# LifeOS – Testing Strategy & Quality Assurance

## 1. Principles
Every component, model, route, and configuration must be verified by automated tests. Tests run within isolated in-memory or transactional scopes to ensure zero cross-test contamination and high execution speed.

## 2. Test Suites
Located in `backend/tests/`:
1. `test_health.py`: Verifies liveness `/api/v1/health` and standard 404 handler.
2. `test_readiness.py`: Verifies database connectivity check `/api/v1/ready` and request ID header tracing.
3. `test_auth.py`: Tests user registration, weak password validation, duplicate email rejection, login verification, token refresh, and unauthenticated request blocks.
4. `test_security.py`: Tests resource ownership checking utilities and refresh token revocation / logout flow.
5. `test_pagination.py`: Tests query pagination boundaries, total page calculations, and `max_per_page` clamping.
6. `test_config.py`: Tests Development, Testing, and Production configuration validation rules.
7. `test_error_handling.py`: Tests domain exception serialization and 405 Method Not Allowed handling.
8. `test_models.py`: Tests complete domain instantiation across all 14 models and validates cascade deletion semantics.

## 3. Running Test Suites
```bash
# Run complete test suite with coverage
cd backend
.\.venv\Scripts\pytest.exe -v --cov=app

# Run specific test module
.\.venv\Scripts\pytest.exe tests/test_security.py -v
```

## 4. Current Quality Metrics
- Total Tests: **21**
- Test Status: **21 passed (100%)**
- Code Coverage: **93%**

