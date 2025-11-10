# CI/CD Pipeline Implementation - Continuation Prompt

**Project**: Guess The Worth (see README.md in root for project details)

**Current Branch**: `cicd-pipeline` (branched from `dev`)

**Current State**:
- All linting/formatting tool dependencies have been added to `backend/requirements.txt` and `frontend/package.json`
- Configuration files created: `backend/.flake8`, `backend/pyproject.toml`, `backend/.bandit`, `frontend/.prettierrc`, `frontend/.prettierignore`
- `frontend/vite.config.js` updated with test coverage configuration
- All changes are committed
- Project runs successfully with new dependencies installed

---

## IMMEDIATE TASK: Auto-Fix Code with Formatters

Run formatters and commit each separately:

1. **Backend - Black formatter**:
   - Run: `cd backend && black .`
   - Review changes, commit: "chore: format backend code with black"

2. **Backend - isort**:
   - Run: `cd backend && isort .`
   - Review changes, commit: "chore: organize backend imports with isort"

3. **Frontend - Prettier**:
   - Run: `cd frontend && npm run format`
   - Review changes, commit: "chore: format frontend code with prettier"

After auto-fixing is complete, proceed with Phase 1.

---

## CI/CD IMPLEMENTATION PHASES

### Phase 1: Backend CI Foundation
**Goal**: Get backend linting, testing, and Docker build in CI

**Tasks**:
1. Create `.github/workflows/backend-ci.yml`
2. Configure to trigger on push/PR to `main` and `dev` branches
3. Implement jobs:
   - **Code Quality Job**:
     - Install dependencies
     - Run `black --check backend/`
     - Run `flake8 backend/`
     - Run `isort --check-only backend/`
   - **Test Job**:
     - Set up PostgreSQL service container
     - Install dependencies
     - Run `pytest backend/tests/ --cov --cov-report=xml`
     - **IMPORTANT**: Initially allow 0% coverage (no tests exist yet)
   - **Docker Build Job**:
     - Build backend Docker image tagged with `${{ github.sha }}`
     - Don't push to registry yet (Phase 5)

**Deliverable**: Backend CI workflow runs on every push/PR

---

### Phase 2: Frontend CI Foundation
**Goal**: Get frontend linting, testing, and build in CI

**Tasks**:
1. Create `.github/workflows/frontend-ci.yml`
2. Configure to trigger on push/PR to `main` and `dev` branches
3. Implement jobs:
   - **Code Quality Job**:
     - Run `npm ci` in frontend directory
     - Run `npm run lint`
     - Run `npm run format:check`
   - **Test Job**:
     - Run `npm run test -- --coverage`
     - **IMPORTANT**: Initially allow 0% coverage
   - **Build Job**:
     - Run `npm run build`
     - Verify build succeeds

**Deliverable**: Frontend CI workflow runs on every push/PR

---

### Phase 3: Security Scanning
**Goal**: Add security checks to both CI pipelines

**Backend Security** (add to backend-ci.yml):
- New job: **Security Job**
  - Run `bandit -r backend/`
  - Run `pip-audit`
  - Run TruffleHog to scan for secrets: `trufflehog filesystem backend/ --fail`
  - Run Trivy scan on Docker image: `trivy image backend:${{ github.sha }}`

**Frontend Security** (add to frontend-ci.yml):
- New job: **Security Job**
  - Run `npm audit --audit-level=high`
  - Optional: Run Trivy on frontend Docker image

**Deliverable**: Security scanning integrated into both CI workflows

---

### Phase 4: Test Coverage Reporting
**Goal**: Set up Codecov integration for coverage reports

**Tasks**:
1. Sign up for Codecov account (codecov.io)
2. Connect GitHub repository to Codecov
3. Add Codecov upload to backend test job:
   ```yaml
   - uses: codecov/codecov-action@v4
     with:
       file: ./coverage.xml
       flags: backend
   ```
4. Add Codecov upload to frontend test job:
   ```yaml
   - uses: codecov/codecov-action@v4
     with:
       file: ./coverage/lcov.info
       flags: frontend
   ```
5. Configure Codecov to show coverage on PRs
6. **NOTE**: Keep 0% coverage passing for now - will enforce 70% threshold later after tests are written

**Deliverable**: Coverage reports visible on PRs via Codecov

---

### Phase 5: GitHub Container Registry (GHCR)
**Goal**: Push Docker images to GHCR after successful builds

**Tasks**:
1. Add GHCR login and push to backend-ci.yml (only on `main` branch):
   ```yaml
   - name: Log in to GHCR
     uses: docker/login-action@v3
     with:
       registry: ghcr.io
       username: ${{ github.actor }}
       password: ${{ secrets.GITHUB_TOKEN }}

   - name: Push to GHCR
     run: |
       docker tag backend:${{ github.sha }} ghcr.io/${{ github.repository }}/backend:latest
       docker tag backend:${{ github.sha }} ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
       docker push ghcr.io/${{ github.repository }}/backend:latest
       docker push ghcr.io/${{ github.repository }}/backend:${{ github.sha }}
   ```

2. Add same for frontend (if using Docker for frontend deployment)

**Deliverable**: Docker images pushed to GHCR on successful builds to `main`

---

### Phase 6: Branch Protection Rules
**Goal**: Enforce CI checks before merging to main

**Tasks**:
1. Go to GitHub repo Settings → Branches → Add rule for `main`
2. Enable:
   - Require pull request reviews (at least 1 approval)
   - Require status checks to pass:
     - Backend CI: All jobs must pass
     - Frontend CI: All jobs must pass
   - Require branches to be up to date before merging
   - Do not allow force pushes
   - Require linear history
3. Optional: Create similar (lighter) rules for `dev` branch

**Deliverable**: Cannot merge to `main` without passing CI and review

---

### Phase 7: Continuous Deployment
**Goal**: Auto-deploy to environments

**PREREQUISITE**: Choose deployment platform first. Ask user for preference:
- Render (recommended - easy setup, free tier)
- Railway
- Fly.io
- Cloud provider (Azure/AWS/GCP)
- Other

**Tasks** (platform-specific implementation):
1. Create `.github/workflows/deploy.yml`
2. Configure deployment triggers:
   - Dev environment: Auto-deploy from `dev` branch
   - Production: Auto-deploy from `main` branch OR manual approval
3. Backend deployment steps:
   - Build/pull Docker image from GHCR
   - Deploy to platform
   - Run database migrations: `alembic upgrade head`
   - Health check: Verify `/health` endpoint
   - Smoke tests (basic API checks)
   - Rollback on failure
4. Frontend deployment steps:
   - Build with production env vars
   - Deploy static files
   - Verify deployment with HTTP check

**Deliverable**: Automated deployment pipeline for both environments

---

### Phase 8: Monitoring & Observability
**Goal**: Set up error tracking and monitoring

**Tasks**:
1. **Health Check Endpoints** (add to backend):
   - Create `backend/routers/health.py`
   - Implement `/health` and `/health/db` endpoints

2. **Sentry Setup**:
   - Sign up for Sentry (free tier)
   - Install SDK in backend: `pip install sentry-sdk`
   - Install SDK in frontend: `npm install @sentry/react`
   - Configure with DSN from environment variables
   - Test error reporting

3. **Uptime Monitoring**:
   - Sign up for UptimeRobot (free tier)
   - Add monitors for production URLs
   - Configure alerts

4. **Create CODEOWNERS file**:
   - Define automatic review assignments

**Deliverable**: Full observability stack for production

---

## IMPORTANT NOTES

1. **Coverage Threshold**: Keep at 0% for all phases. Will change to 70% requirement ONLY after comprehensive tests are written (separate initiative from CI/CD setup)

2. **Deployment Platform**: Phase 7 requires deployment platform decision before implementation

3. **Commit Messages**: Use conventional commit format:
   - `feat:` New feature
   - `fix:` Bug fix
   - `chore:` Maintenance/tooling
   - `ci:` CI/CD changes
   - `test:` Test changes

4. **Testing**: Don't run formatters after auto-fix tasks - code should remain formatted

5. **Branch Strategy**: Work on `cicd-pipeline` branch, merge to `dev` when phases are complete, then `dev` → `main` after testing

---

**START HERE**: Run the auto-fix tasks first, then begin Phase 1.
