# CI/CD Implementation Guide

Complete guide for implementing Continuous Integration and Continuous Deployment for Guess The Worth.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Implementation Phases](#implementation-phases)
4. [Current Status](#current-status)
5. [Next Steps](#next-steps)

## Overview

This project uses a multi-phase approach to implement a robust CI/CD pipeline:

- **CI (Continuous Integration):** Automated testing, linting, and building on every commit
- **CD (Continuous Deployment):** Automated deployment to staging and production environments

### Technology Stack

**Backend:** FastAPI + Python 3.11 + PostgreSQL
**Frontend:** React 19 + Vite + Chakra UI
**CI/CD:** GitHub Actions
**Containers:** Docker + Docker Compose
**Hosting:** Render.com
**Database:** Managed PostgreSQL

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Developer Workflow                          │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │  Git Push/PR   │
         └────────┬───────┘
                  │
                  ▼
    ┌──────────────────────────────────┐
    │      GitHub Actions (CI)         │
    ├──────────────────────────────────┤
    │  1. Code Quality (lint/format)   │
    │  2. Security Scanning            │
    │  3. Unit & Integration Tests     │
    │  4. Build & Containerize         │
    │  5. Coverage Reporting           │
    └──────────────┬───────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  Quality Gates  │
         │  ✓ Tests Pass   │
         │  ✓ Coverage OK  │
         │  ✓ No Secrets   │
         └────────┬────────┘
                  │
                  ▼
    ┌──────────────────────────────────┐
    │   Continuous Deployment (CD)     │
    ├──────────────────────────────────┤
    │  1. Database Migrations          │
    │  2. Deploy to Staging (auto)     │
    │  3. Deploy to Production (manual)│
    │  4. Health Checks                │
    └──────────────┬───────────────────┘
                   │
                   ▼
         ┌─────────────────┐
         │  Live Services  │
         └─────────────────┘
```

## Implementation Phases

### ✅ Phase 1: Foundation & Code Quality (COMPLETED)

**Status:** Ready to use

**What's included:**
- Backend linting (black, flake8, mypy, isort)
- Comprehensive test structure
- Pre-commit hooks
- Initial test coverage

**Files created:**
- [backend/pyproject.toml](../backend/pyproject.toml) - Python tool configuration
- [backend/.flake8](../backend/.flake8) - Linting rules
- [backend/tests/](../backend/tests/) - Test suite
- [.pre-commit-config.yaml](../.pre-commit-config.yaml) - Git hooks
- [frontend/src/components/__tests__/](../frontend/src/components/__tests__/) - Component tests

**Documentation:**
- [Phase 1 Setup Guide](./PHASE1_SETUP_GUIDE.md)

**Usage:**
```bash
# Install dependencies
cd backend && pip install -r requirements.txt
cd frontend && npm install

# Install pre-commit
pip install pre-commit
pre-commit install

# Run tests
cd backend && pytest --cov
cd frontend && npm test
```

---

### ⏳ Phase 2: GitHub Actions CI Workflow (TODO)

**Goal:** Automated testing and building on every push/PR

**Files to create:**
- `.github/workflows/ci.yml` - Main CI workflow
- `.github/workflows/pr-checks.yml` - PR-specific checks
- `.github/dependabot.yml` - Dependency updates

**Workflow stages:**

#### 1. Frontend Quality Job
```yaml
- Checkout code
- Setup Node.js 20 with cache
- Install dependencies
- Run ESLint
- Run Vitest tests with coverage
- Upload coverage to Codecov
- Build production bundle
```

#### 2. Backend Quality Job
```yaml
- Checkout code
- Setup Python 3.11 with cache
- Install dependencies
- Run black --check
- Run flake8
- Run mypy
- Run pytest with coverage
- Upload coverage to Codecov
```

#### 3. Integration Tests Job
```yaml
- Start PostgreSQL service
- Run database migrations
- Run E2E tests (optional)
```

**Quality gates (must pass):**
- All tests passing
- Coverage > 80%
- No linting errors
- No high/critical security issues

---

### ⏳ Phase 3: Docker Build & Security (TODO)

**Goal:** Production-ready containers with security scanning

**Files to create/update:**
- `backend/Dockerfile.prod` - Multi-stage production build
- `frontend/Dockerfile.prod` - Multi-stage with Nginx
- `frontend/nginx.conf` - Production web server config
- `docker-compose.prod.yml` - Production compose file
- `.github/workflows/docker-build.yml` - Container build workflow

**Improvements:**

#### Backend Dockerfile (Multi-stage)
```dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "main:socket_app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile (Multi-stage + Nginx)
```dockerfile
FROM node:20-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Security scanning:**
- Trivy for container vulnerabilities
- Snyk for dependency scanning
- Secret detection (detect-secrets)

---

### ⏳ Phase 4: Continuous Deployment (TODO)

**Goal:** Automated deployments with zero-downtime

**Files to create:**
- `.github/workflows/deploy-staging.yml` - Auto-deploy to staging
- `.github/workflows/deploy-production.yml` - Manual deploy to prod
- `scripts/migrate.sh` - Database migration script
- `scripts/health-check.sh` - Health verification

**Deployment strategy:**

#### Staging (Auto-deploy from `develop` branch)
```yaml
1. Run database migrations (Alembic)
2. Build and push Docker images
3. Deploy to Render staging environment
4. Run smoke tests
5. Notify team (Slack/Discord)
```

#### Production (Manual approval from `main` branch)
```yaml
1. Require manual approval from maintainer
2. Create deployment tag
3. Run database migrations
4. Deploy with blue-green strategy
5. Health checks
6. Rollback on failure
```

**Environments:**
- `staging` - Auto-deploy from develop branch
- `production` - Manual deploy from main branch

---

### ⏳ Phase 5: Monitoring & Observability (TODO)

**Goal:** Track performance and errors

**Files to create:**
- `backend/middleware/logging.py` - Structured logging
- `backend/middleware/metrics.py` - Performance metrics
- `.github/workflows/security.yml` - Security scanning

**Add to backend:**
```python
# Health check endpoints
@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/readiness")
async def readiness(db: Session = Depends(get_db)):
    # Check DB connection
    try:
        db.execute("SELECT 1")
        return {"status": "ready"}
    except:
        raise HTTPException(status_code=503)
```

**Optional integrations:**
- Sentry for error tracking
- Codecov for coverage visualization
- GitHub Code Scanning (CodeQL)

---

## Current Status

### ✅ Completed

- [x] Backend development dependencies added
- [x] Backend linting configuration (black, flake8, mypy, isort)
- [x] Backend test structure with fixtures
- [x] Initial backend tests (auth, artworks, bids, database)
- [x] Frontend component tests (Header, LiveAuctions)
- [x] Pre-commit hooks setup
- [x] Secret detection baseline
- [x] Documentation

### ⏳ In Progress

- [ ] GitHub Actions CI workflow
- [ ] Code coverage integration
- [ ] Docker production builds

### 📋 Todo

- [ ] Container security scanning
- [ ] Deployment workflows
- [ ] Database migration automation
- [ ] E2E tests (Playwright/Cypress)
- [ ] Monitoring setup

## Next Steps

### Immediate Actions (Do These Now)

1. **Install and test the foundation:**
   ```bash
   # Install backend dependencies
   cd backend
   pip install -r requirements.txt

   # Run tests to verify setup
   pytest --cov

   # Install pre-commit hooks
   pip install pre-commit
   pre-commit install

   # Test pre-commit on existing files
   pre-commit run --all-files
   ```

2. **Fix any linting issues:**
   ```bash
   cd backend
   black .
   isort .
   flake8 .
   ```

3. **Verify frontend tests:**
   ```bash
   cd frontend
   npm test
   ```

### Week 1: CI Setup

1. Create `.github/workflows/ci.yml` for automated testing
2. Setup Codecov account and get token
3. Add GitHub secrets for CI
4. Test workflow on a feature branch
5. Add branch protection rules

### Week 2: Docker & Security

1. Create production Dockerfiles
2. Setup Docker Hub account
3. Add container build workflow
4. Add Trivy security scanning
5. Test local builds

### Week 3: Deployment

1. Setup Render account
2. Create staging and production environments
3. Add deployment workflows
4. Test database migrations
5. Create deployment documentation

## Quality Gates

Before code can be merged to `main`, it must pass:

- ✅ All tests passing (backend + frontend)
- ✅ Code coverage maintained or improved
- ✅ No linting errors
- ✅ No high/critical security vulnerabilities
- ✅ Pre-commit hooks passing
- ✅ PR approved by maintainer
- ✅ Branch up-to-date with main

## Branching Strategy

```
main (production)
  └── develop (staging)
      ├── feature/auction-system
      ├── feature/payment-integration
      └── bugfix/bid-validation
```

**Workflow:**
1. Create feature branch from `develop`
2. Make changes, commit (pre-commit runs)
3. Push and create PR to `develop`
4. CI runs on PR (tests, lint, build)
5. After approval, merge to `develop` (auto-deploy to staging)
6. Test on staging
7. Create PR from `develop` to `main`
8. After approval, merge to `main` (manual deploy to production)

## Environment Variables

### Required GitHub Secrets

**For CI:**
- `CODECOV_TOKEN` - Code coverage reporting

**For Docker Build:**
- `DOCKER_USERNAME` - Docker Hub username
- `DOCKER_PASSWORD` - Docker Hub password

**For Deployment:**
- `RENDER_API_KEY` - Render deployment
- `DATABASE_URL_STAGING` - Staging database
- `DATABASE_URL_PRODUCTION` - Production database
- `AUTH0_CLIENT_SECRET` - Auth0 configuration
- `STRIPE_SECRET_KEY` - Payment processing
- `SECRET_KEY_PRODUCTION` - JWT signing

## Metrics & Monitoring

### Target Metrics

- **CI Runtime:** < 10 minutes
- **Deployment Time:** < 5 minutes
- **Test Coverage:** > 80%
- **Build Success Rate:** > 95%
- **Deployment Success Rate:** > 98%

### Monitoring

- GitHub Actions status badges
- Codecov coverage reports
- Render deployment logs
- Sentry error tracking (optional)

## Troubleshooting

### Common Issues

**Pre-commit hooks fail:**
```bash
# Fix formatting
cd backend && black . && isort .
cd frontend && npm run lint

# Retry commit
git commit -m "Your message"
```

**Tests fail locally:**
```bash
# Backend
cd backend
pytest -v  # Verbose output

# Frontend
cd frontend
npm test -- --reporter=verbose
```

**Docker build fails:**
```bash
# Check Docker daemon
docker info

# Build locally
docker build -t test-build -f backend/Dockerfile backend/
```

## Resources

- [Phase 1 Setup Guide](./PHASE1_SETUP_GUIDE.md)
- [Testing Guide](./TESTING.md) (to be created)
- [Deployment Guide](./DEPLOYMENT.md) (to be created)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Render Docs](https://render.com/docs)

---

**Questions or issues?** Open a GitHub issue or check the individual phase guides.
