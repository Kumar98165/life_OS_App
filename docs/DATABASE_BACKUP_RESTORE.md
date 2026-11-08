# LifeOS Database Backup & Restore Guide

> **Version**: 1.0.0  
> **Last Updated**: 2026-11-08  
> **Database**: PostgreSQL (lifeos_db)  
> **Migration Tool**: Alembic (via Flask-Migrate)

---

## 1. Migration History

| # | Revision | Description |
|---|----------|-------------|
| 1 | `da6fd72948d3` | Create users table |
| 2 | `fd75471a4d7c` | Add complete database architecture (Tasks, Goals, Habits, AI) |
| 3 | `daaa4c2c151c` | Add planner block fields |
| 4 | `e3bb8a0112fa` | Add goal priority and milestone description |
| 5 | `87ec6f9980ac` | Add AI memory fields and preference |
| 6 | `05e04b80ec43` | Add AI learning, feedback, and evaluations |
| 7 | `ee971e5ed97a` | Add activated_at to AI prompt versions |
| 8 | `24a8f1665cef` | Add Step 14 finance tables and columns |
| 9 | `720a5fbf3e06` | Add Step 15 notifications and reminders |

**Current Head**: `720a5fbf3e06`

---

## 2. Checking Migration Status

```bash
# Show current database revision
flask db current

# Check if migrations are up to date
flask db check

# Show migration history
flask db history --verbose
```

---

## 3. Backup Procedures

### 3.1 Full Database Backup (pg_dump)

```bash
# Full backup (custom format — recommended for selective restore)
pg_dump -h localhost -U postgres -d lifeos_db -Fc -f lifeos_backup_$(date +%Y%m%d_%H%M%S).dump

# Full backup (SQL format — human-readable)
pg_dump -h localhost -U postgres -d lifeos_db -f lifeos_backup_$(date +%Y%m%d_%H%M%S).sql

# Schema-only backup
pg_dump -h localhost -U postgres -d lifeos_db --schema-only -f lifeos_schema_$(date +%Y%m%d_%H%M%S).sql

# Data-only backup
pg_dump -h localhost -U postgres -d lifeos_db --data-only -f lifeos_data_$(date +%Y%m%d_%H%M%S).sql
```

### 3.2 Table-Specific Backup

```bash
# Backup specific tables (e.g., finance)
pg_dump -h localhost -U postgres -d lifeos_db \
  -t financial_accounts \
  -t financial_transactions \
  -t financial_categories \
  -t budgets \
  -t savings_goals \
  -Fc -f lifeos_finance_$(date +%Y%m%d_%H%M%S).dump
```

### 3.3 Automated Backup Script

Create `scripts/backup.sh`:

```bash
#!/bin/bash
# LifeOS Database Backup Script
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/lifeos}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_USER="${DB_USER:-postgres}"
DB_NAME="${DB_NAME:-lifeos_db}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/lifeos_${TIMESTAMP}.dump"

# Create backup
echo "[$(date)] Starting backup..."
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -Fc -f "$BACKUP_FILE"
echo "[$(date)] Backup created: $BACKUP_FILE ($(du -h $BACKUP_FILE | cut -f1))"

# Cleanup old backups
echo "[$(date)] Removing backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "lifeos_*.dump" -mtime +$RETENTION_DAYS -delete

echo "[$(date)] Backup complete."
```

### 3.4 Cron Schedule (Production)

```bash
# Daily backup at 2:00 AM
0 2 * * * /path/to/scripts/backup.sh >> /var/log/lifeos_backup.log 2>&1
```

---

## 4. Restore Procedures

### 4.1 Full Restore from Custom Format

```bash
# Drop and recreate database
dropdb -h localhost -U postgres lifeos_db
createdb -h localhost -U postgres lifeos_db

# Restore from dump
pg_restore -h localhost -U postgres -d lifeos_db lifeos_backup_20261108.dump

# Verify migration state
flask db current
```

### 4.2 Full Restore from SQL Format

```bash
dropdb -h localhost -U postgres lifeos_db
createdb -h localhost -U postgres lifeos_db
psql -h localhost -U postgres -d lifeos_db < lifeos_backup_20261108.sql
```

### 4.3 Selective Table Restore

```bash
# Restore only specific tables (data only, append to existing)
pg_restore -h localhost -U postgres -d lifeos_db \
  --data-only \
  -t financial_transactions \
  lifeos_backup_20261108.dump
```

---

## 5. Migration Operations

### 5.1 Apply Pending Migrations

```bash
# Upgrade to latest
flask db upgrade

# Upgrade to specific revision
flask db upgrade 720a5fbf3e06
```

### 5.2 Downgrade (Rollback)

> [!CAUTION]
> Always backup before downgrading. Downgrades may drop columns and lose data.

```bash
# Downgrade one step
flask db downgrade -1

# Downgrade to specific revision
flask db downgrade ee971e5ed97a

# Downgrade all (returns to empty schema)
flask db downgrade base
```

### 5.3 Generate New Migration

```bash
# Auto-generate migration from model changes
flask db migrate -m "description of changes"

# Review generated migration before applying
# File: backend/migrations/versions/<revision>_<description>.py

# Apply the migration
flask db upgrade
```

---

## 6. Disaster Recovery Procedure

### Step-by-Step Recovery

1. **Stop the application**
   ```bash
   # Stop Gunicorn / Flask process
   systemctl stop lifeos
   ```

2. **Restore database**
   ```bash
   dropdb -h localhost -U postgres lifeos_db
   createdb -h localhost -U postgres lifeos_db
   pg_restore -h localhost -U postgres -d lifeos_db /var/backups/lifeos/latest.dump
   ```

3. **Verify migration state**
   ```bash
   flask db current
   # Should show: 720a5fbf3e06 (head)
   ```

4. **Apply any pending migrations** (if app was upgraded since backup)
   ```bash
   flask db upgrade
   ```

5. **Verify data integrity**
   ```bash
   psql -h localhost -U postgres -d lifeos_db -c "
     SELECT 'users' as tbl, count(*) FROM users
     UNION ALL
     SELECT 'tasks', count(*) FROM tasks
     UNION ALL
     SELECT 'financial_transactions', count(*) FROM financial_transactions
     UNION ALL
     SELECT 'notifications', count(*) FROM notifications;
   "
   ```

6. **Restart the application**
   ```bash
   systemctl start lifeos
   ```

---

## 7. Database Health Checks

```sql
-- Check table sizes
SELECT relname AS table, pg_size_pretty(pg_total_relation_size(relid)) AS size
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Check index usage
SELECT schemaname, relname, indexrelname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Check for unused indexes
SELECT schemaname, relname, indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
AND indexrelname NOT LIKE '%_pkey';

-- Check connection count
SELECT count(*) FROM pg_stat_activity WHERE datname = 'lifeos_db';

-- Check active locks
SELECT * FROM pg_locks WHERE NOT granted;
```

---

## 8. Important Notes

> [!IMPORTANT]
> - Always test restore procedures in a non-production environment before relying on them.
> - The `alembic_version` table is included in backups and tracks migration state.
> - UUID primary keys ensure no ID conflicts during partial restores.
> - Financial data uses `Numeric(14,2)` — precision is preserved in pg_dump/pg_restore.
