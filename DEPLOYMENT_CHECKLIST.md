# Production Deployment Checklist

Use this checklist to ensure safe and successful production deployments.

## Pre-Deployment (Development)

### Code Quality
- [ ] All tests passing locally (`pytest` and `npm test`)
- [ ] No linting errors (`flake8`, `black --check`, `isort --check`)
- [ ] Code formatted (`black .`, `isort .`, `prettier --write .`)
- [ ] No `console.log` or debugging code in production builds
- [ ] No hardcoded secrets or credentials
- [ ] No commented-out code blocks

### Testing
- [ ] Backend test coverage ≥80%
  ```bash
  cd backend && pytest --cov --cov-fail-under=80
  ```
- [ ] Frontend test coverage ≥70%
  ```bash
  cd frontend && npm run test:coverage
  ```
- [ ] Critical paths (auth, bidding) ≥90% coverage
- [ ] E2E tests passing
  ```bash
  cd backend && pytest tests/e2e/ -v
  ```
- [ ] Migration rollback tested
  ```bash
  cd backend && ./scripts/test_migrations.sh
  ```

### Security
- [ ] All secrets moved to environment variables
- [ ] `.gitignore` properly configured (`.env`, `node_modules/`, etc.)
- [ ] No secrets committed to git history
  ```bash
  git secrets --scan-history  # Or use gitleaks/trufflehog
  ```
- [ ] Rate limiting enabled on critical endpoints
- [ ] Audit logging enabled and tested
- [ ] Security headers configured (CSP, X-Frame-Options, etc.)
- [ ] HTTPS enforced (no HTTP in production)
- [ ] CORS properly configured with production domains
- [ ] Security scan passed:
  ```bash
  cd backend && bandit -r . --severity-level medium
  cd backend && pip-audit --desc
  cd frontend && npm audit --audit-level=high
  ```

### Database
- [ ] Backup created:
  ```bash
  cd backend && ./scripts/backup_database.sh
  ```
- [ ] Migrations tested:
  ```bash
  cd backend && ./scripts/test_migrations.sh
  ```
- [ ] Database indexes verified
- [ ] Connection pooling configured
- [ ] Database credentials rotated for production

---

## Deployment

### Environment Configuration
- [ ] Production `.env` files created (NOT committed to git)
- [ ] `DATABASE_URL` points to production database
- [ ] `AUTH0_CLIENT_SECRET` is production secret (not development)
- [ ] `JWT_SECRET_KEY` is strong random key:
  ```bash
  openssl rand -hex 32
  ```
- [ ] `ALLOWED_ORIGINS` / `CORS_ORIGINS` includes production domain
- [ ] `STRIPE_SECRET_KEY` is production key (if using Stripe)
- [ ] `ENVIRONMENT` set to `production`
- [ ] All environment variables documented

### Database Migration
1. [ ] Create production database backup
   ```bash
   ./scripts/backup_database.sh
   # Save backup file name: db_backup_YYYYMMDD_HHMMSS.sql
   ```
2. [ ] Run migrations:
   ```bash
   alembic upgrade head
   ```
3. [ ] Verify migration:
   ```bash
   alembic current  # Should show (head)
   ```
4. [ ] Test application connections
   ```bash
   curl https://api.yourdomain.com/health
   ```

### Application Deployment
- [ ] Backend built and deployed
  ```bash
  docker build -t backend:latest ./backend
  docker push your-registry/backend:latest
  ```
- [ ] Frontend built:
  ```bash
  cd frontend && npm run build
  ```
- [ ] Frontend deployed (static files served via CDN/Azure Static Web Apps)
- [ ] Web server configured for SPA routing (handle 404 → index.html)
- [ ] SSL/TLS certificate installed and valid
- [ ] DNS records updated (if domain changed)

### Verification
- [ ] Health check endpoint responding:
  ```bash
  curl https://api.yourdomain.com/health
  ```
- [ ] Admin health endpoint responding:
  ```bash
  curl -H "Authorization: Bearer <admin_token>" \
       https://api.yourdomain.com/api/admin/system/health
  ```
- [ ] Authentication working (Auth0 login flow)
- [ ] WebSocket connections working (real-time bidding)
- [ ] Image uploads working
- [ ] Database queries performing well (check logs)
- [ ] No errors in application logs
- [ ] Rate limiting active (test by exceeding limits)

---

## Post-Deployment

### Monitoring
- [ ] Error logging configured (Sentry, LogRocket, etc.)
- [ ] Performance monitoring enabled (New Relic, Datadog, APM)
- [ ] Database monitoring active (Azure DB Insights, pgAdmin)
- [ ] Alert notifications configured (email, Slack, PagerDuty)
- [ ] Uptime monitoring configured (UptimeRobot, Pingdom)
- [ ] Log aggregation setup (Azure Monitor, CloudWatch, ELK)

### Testing
- [ ] Smoke tests on production
- [ ] User registration works
  ```
  Test: Register new user → Receive confirmation → Login
  ```
- [ ] Artwork creation works
  ```
  Test: Login as seller → Create artwork → Verify appears in gallery
  ```
- [ ] Bidding works
  ```
  Test: Login as buyer → Place bid → Verify bid recorded
  ```
- [ ] Admin dashboard accessible
  ```
  Test: Login as admin → View stats → Access audit logs
  ```
- [ ] Real-time updates working
  ```
  Test: Open 2 browsers → Place bid in one → Verify update in other
  ```

### Documentation
- [ ] Production URLs documented
- [ ] Admin credentials securely stored (password manager, Azure Key Vault)
- [ ] Backup schedule documented
- [ ] Incident response plan defined
- [ ] Runbook created for common operations
- [ ] Team members have necessary access

---

## Rollback Plan

If deployment fails, follow these steps:

### 1. Immediate Rollback

- [ ] Revert application to previous version
  ```bash
  # Docker
  docker pull your-registry/backend:previous-tag
  docker pull your-registry/frontend:previous-tag

  # Or use git
  git checkout <previous-commit>
  git push --force
  ```
- [ ] Rollback database:
  ```bash
  alembic downgrade -1
  ```
- [ ] Verify old version works
  ```bash
  curl https://api.yourdomain.com/health
  ```

### 2. If Database Corrupted

- [ ] Stop application to prevent further damage
- [ ] Restore from backup:
  ```bash
  # Restore PostgreSQL backup
  psql -U postgres -d guess_the_worth_db < backups/db_backup_YYYYMMDD_HHMMSS.sql
  ```
- [ ] Verify data integrity:
  ```bash
  # Check critical tables
  psql -U postgres -d guess_the_worth_db -c "SELECT COUNT(*) FROM users;"
  psql -U postgres -d guess_the_worth_db -c "SELECT COUNT(*) FROM artworks;"
  ```
- [ ] Restart application

### 3. Communication

- [ ] Notify team of rollback (Slack, email)
- [ ] Update status page (if applicable)
- [ ] Document what failed and why
- [ ] Create postmortem document
- [ ] Schedule fix and re-deployment

---

## Production Health Checks

### Daily Checks
- [ ] Application uptime >99%
- [ ] No error spikes in logs
- [ ] Database connections stable
- [ ] API response times <500ms
- [ ] Disk space >20% free

### Weekly Checks
- [ ] Security scan (dependencies updated)
- [ ] Database backup verified (test restore)
- [ ] SSL certificate validity >30 days
- [ ] Review audit logs for suspicious activity

### Monthly Checks
- [ ] Disaster recovery drill (test full restore)
- [ ] Performance review (identify bottlenecks)
- [ ] Security patches applied
- [ ] Dependencies updated
- [ ] Review and rotate secrets/credentials

---

## Sign-Off

**Deployment Details:**
- **Deployed by:** ________________
- **Verified by:** ________________
- **Date:** ________________
- **Time:** ________________
- **Production URL:** ________________
- **Backend Version/Tag:** ________________
- **Frontend Version/Tag:** ________________
- **Database Backup:** ________________

**Verification Checklist:**
- [ ] All tests passed
- [ ] Security scan passed
- [ ] Health endpoints responding
- [ ] Authentication working
- [ ] Real-time features working
- [ ] Monitoring active
- [ ] Team notified

**Rollback Information:**
- **Previous Backend Version:** ________________
- **Previous Frontend Version:** ________________
- **Database Backup Location:** ________________

---

**Notes:**
_Add any deployment-specific notes, warnings, or observations here._

---

**Last Updated:** 2025-11-23
**Template Version:** 1.0
