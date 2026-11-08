# LifeOS Production Configuration Guide

> **Version**: 1.0.0  
> **Last Updated**: 2026-11-08

---

## 1. Backend Environment Variables

### Required Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| `FLASK_ENV` | Application mode | `production` | ✅ |
| `SECRET_KEY` | Flask session signing key (32+ chars) | `<random-hex-string>` | ✅ |
| `JWT_SECRET_KEY` | JWT token signing key (32+ chars) | `<random-hex-string>` | ✅ |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://user:pass@host:5432/lifeos_db` | ✅ |

### Optional Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `5000` | Server port |
| `JWT_ACCESS_TOKEN_EXPIRES_SEC` | `3600` | Access token TTL (seconds) |
| `JWT_REFRESH_TOKEN_EXPIRES_SEC` | `2592000` | Refresh token TTL (30 days) |
| `MAX_CONTENT_LENGTH` | `10485760` | Max request body (10MB) |
| `CORS_ALLOWED_ORIGINS` | `*` | Comma-separated allowed origins |
| `LOG_LEVEL` | `INFO` | Logging level |
| `RATELIMIT_DEFAULT` | `1000 per hour,100 per minute` | Global rate limits |
| `RATELIMIT_STORAGE_URI` | `memory://` | Rate limiter backend |
| `RATELIMIT_STRATEGY` | `fixed-window` | Rate limiting strategy |
| `DB_POOL_SIZE` | `10` | SQLAlchemy pool size |
| `DB_MAX_OVERFLOW` | `20` | Pool overflow connections |
| `DB_POOL_RECYCLE` | `1800` | Pool connection recycle (seconds) |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL |
| `OLLAMA_MODEL` | `qwen2.5:3b` | Target LLM model |
| `OLLAMA_TIMEOUT` | `60` | LLM request timeout (seconds) |
| `OLLAMA_TEMPERATURE` | `0.7` | LLM temperature |
| `OLLAMA_MAX_TOKENS` | `1024` | Max response tokens |
| `TEST_DATABASE_URL` | `sqlite:///:memory:` | Test database URL |

### Production Validation

The `ProductionConfig` class automatically validates at startup:

```python
# backend/app/config.py
class ProductionConfig(BaseConfig):
    DEBUG = False

    @classmethod
    def validate_production(cls):
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise ValueError("DATABASE_URL must be set")
        if cls.SECRET_KEY in ["dev-secret-key-change-in-production-32chars", "", None]:
            raise ValueError("A secure SECRET_KEY must be provided")
        if cls.JWT_SECRET_KEY in ["jwt-secret-key-change-in-production-32chars", "", None]:
            raise ValueError("A secure JWT_SECRET_KEY must be provided")
```

---

## 2. Mobile Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `EXPO_PUBLIC_API_URL` | Backend API base URL | `https://api.lifeos.example.com/api/v1` |
| `EXPO_PUBLIC_APP_ENV` | App environment | `production` |

### Platform-Specific API URLs

| Platform | Default URL | Notes |
|----------|-------------|-------|
| Android Emulator | `http://10.0.2.2:5000/api/v1` | Android emulator host alias |
| iOS Simulator | `http://localhost:5000/api/v1` | Direct localhost |
| Physical Device | `http://<LAN_IP>:5000/api/v1` | Local network IP |
| Production | `https://api.lifeos.example.com/api/v1` | HTTPS required |

---

## 3. CORS Configuration

### Development (default)
```
CORS_ALLOWED_ORIGINS=*
```

### Production (recommended)
```
CORS_ALLOWED_ORIGINS=https://lifeos.example.com,https://app.lifeos.example.com
```

> [!WARNING]
> Never use `CORS_ALLOWED_ORIGINS=*` in production. Restrict to your known frontend origins.

---

## 4. Rate Limiting

### Global Defaults
- 1000 requests per hour per IP
- 100 requests per minute per IP

### Auth-Specific Limits
- Register: 10 per minute
- Login: 15 per minute

### Production Rate Limiter Storage

For multi-process deployments, switch from `memory://` to Redis:

```
RATELIMIT_STORAGE_URI=redis://localhost:6379/1
```

---

## 5. Database Connection Pool

| Setting | Default | Recommended Production |
|---------|---------|----------------------|
| `DB_POOL_SIZE` | 10 | 15-25 (based on load) |
| `DB_MAX_OVERFLOW` | 20 | 30-50 |
| `DB_POOL_RECYCLE` | 1800 | 1800 |
| Pool Pre-Ping | True (hardcoded) | Always enabled |

---

## 6. Ollama / Local AI Setup

### Prerequisites
1. Install Ollama: https://ollama.ai
2. Pull the model:
   ```bash
   ollama pull qwen2.5:3b
   ```
3. Verify model availability:
   ```bash
   curl http://localhost:11434/api/tags
   ```

### Health Check
```
GET /api/v1/ai/health
```
Returns `200` with `healthy: true` if operational, `503` if unreachable.

---

## 7. Running in Production

### Backend

```bash
# Set environment
export FLASK_ENV=production
export SECRET_KEY=$(openssl rand -hex 32)
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export DATABASE_URL=postgresql+psycopg2://user:password@host:5432/lifeos_db

# Apply migrations
flask db upgrade

# Run with Gunicorn (recommended)
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"
```

### Mobile (EAS Build)

```bash
# Install EAS CLI
npm install -g eas-cli

# Configure EAS
eas build:configure

# Build for Android
eas build --platform android --profile production

# Build for iOS
eas build --platform ios --profile production
```

---

## 8. Deployment Architecture

```
                    ┌──────────────┐
                    │   Nginx /    │
                    │  Reverse     │
                    │  Proxy       │
                    └──────┬───────┘
                           │
              ┌────────────┴────────────┐
              │                         │
     ┌────────▼─────────┐    ┌─────────▼──────────┐
     │  Flask + Gunicorn │    │  Ollama Runtime     │
     │  (4 workers)      │    │  (qwen2.5:3b)      │
     │  Port 5000        │    │  Port 11434         │
     └────────┬──────────┘    └────────────────────┘
              │
     ┌────────▼──────────┐
     │  PostgreSQL       │
     │  Port 5432        │
     │  lifeos_db        │
     └───────────────────┘
```

---

## 9. Generating Secrets

```bash
# Generate SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"

# Generate JWT_SECRET_KEY
python -c "import secrets; print(secrets.token_hex(32))"
```

> [!CAUTION]
> Never reuse keys between SECRET_KEY and JWT_SECRET_KEY. Never commit secrets to version control.
