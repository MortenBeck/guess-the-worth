# Database Migrations Guide

## Overview
This project uses Alembic for database migrations. This guide covers common operations, rollback procedures, and best practices for managing database schema changes.

## Common Commands

### Create a new migration
```bash
cd backend
alembic revision -m "description_of_changes"
```

### Apply migrations
```bash
alembic upgrade head
```

### Rollback one migration
```bash
alembic downgrade -1
```

### Rollback to specific revision
```bash
alembic downgrade <revision_id>
```

### View migration history
```bash
alembic history
```

### View current migration
```bash
alembic current
```

## Rollback Procedures

### Emergency Rollback

If a migration causes issues in production:

1. **Create backup first:**
   ```bash
   cd backend
   ./scripts/backup_database.sh
   ```

2. **Rollback the migration:**
   ```bash
   alembic downgrade -1
   ```

3. **Verify application works:**
   - Test critical endpoints
   - Check logs for errors
   - Run automated tests

4. **If needed, restore from backup:**
   ```bash
   psql -U postgres -d guess_the_worth_db < backups/db_backup_YYYYMMDD_HHMMSS.sql
   ```

### Testing Migrations Before Production

Always test migrations in development first:

1. **Backup dev database:**
   ```bash
   cd backend
   ./scripts/backup_database.sh
   ```

2. **Test migration:**
   ```bash
   ./scripts/test_migrations.sh
   ```

3. **Verify data integrity:**
   - Check that existing data is preserved
   - Test application functionality
   - Run automated tests: `pytest tests/`

4. **Test rollback:**
   ```bash
   alembic downgrade -1
   alembic upgrade head
   ```

## Docker Environment

When working with Docker containers:

### Test migrations in Docker
```bash
docker exec guess_the_worth_backend bash -c "cd /app && ./scripts/test_migrations.sh"
```

### Create backup from Docker
```bash
docker exec guess_the_worth_backend bash -c "cd /app && ./scripts/backup_database.sh"
```

### Run migrations in Docker
```bash
docker exec guess_the_worth_backend alembic upgrade head
```

### Access the database directly
```bash
docker exec -it guess_the_worth_db psql -U postgres -d guess_the_worth_db
```

## Migration Best Practices

1. **Always create backups** before running migrations in production
2. **Test rollback** in development before deploying
3. **Keep migrations small** and focused on single changes
4. **Never edit applied migrations** - create new ones instead
5. **Include both upgrade() and downgrade()** functions
6. **Test with production-like data volume**
7. **Review auto-generated migrations** - they may need manual adjustments
8. **Document complex migrations** with comments explaining the changes

## Automated Testing

Migrations are tested in the CI/CD pipeline:
- Forward migration (upgrade)
- Backward migration (downgrade)
- Data integrity checks

See [.github/workflows/backend-ci.yml](../../.github/workflows/backend-ci.yml) for details.

## Troubleshooting

### Migration history is out of sync

If your database state doesn't match Alembic's tracking:

```bash
# Check current state
alembic current

# Stamp database to a specific revision without running migrations
alembic stamp <revision_id>

# Or stamp to head
alembic stamp head
```

### Migration conflicts

If you have merge conflicts in migration files:

1. DO NOT manually merge migration files
2. Roll back to the common ancestor
3. Recreate the conflicting migrations on top of the merged branch
4. Use `alembic merge` to create a merge revision if needed

### Database connection issues

Ensure your `.env` file has the correct `DATABASE_URL`:

```bash
DATABASE_URL=postgresql://postgres:password@localhost:5432/guess_the_worth_db
```

For Docker environments, the host should match your container name if running migrations from within Docker.

## Production Deployment Checklist

Before deploying migrations to production:

- [ ] Migration tested in development
- [ ] Rollback tested successfully
- [ ] Database backup created
- [ ] All tests passing
- [ ] Migration reviewed by team
- [ ] Deployment window scheduled (if downtime required)
- [ ] Rollback plan documented
- [ ] Monitoring alerts configured

## Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- Project [README.md](../../README.md)
- [Testing Summary](../../testing_summary.md)

---

**Last Updated:** 2025-11-23
**Maintained by:** Development Team
