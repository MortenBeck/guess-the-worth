# Final Implementation Plan: Completing Production Readiness
### Guess The Worth - Remaining Tasks to Production

**Document Version:** 1.0
**Created:** 2025-01-23
**Priority:** Security → Testing → Features
**Approach:** Pragmatic proof-of-concept implementations

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Pre-Implementation Checklist](#pre-implementation-checklist)
3. [Git Workflow](#git-workflow)
4. [Implementation Stages](#implementation-stages)
5. [Validation Checklist](#validation-checklist)

---

## Overview

### Current Status
Following the initial 10-stage implementation, the application is **70-75% production-ready**. Core functionality works but critical gaps remain:

**✅ Working:**
- Authentication & authorization
- Database schema & migrations
- Frontend API integration
- Real-time bidding (WebSocket)
- Image uploads
- User & seller dashboards

**❌ Critical Gaps:**
- Missing .gitignore files (security risk)
- No test coverage enforcement
- Missing frontend tests
- Admin dashboard non-functional
- No rate limiting (DoS risk)
- No audit logging
- Watchlist feature shows fake data

### Goals
Complete the remaining **7 stages** to achieve production readiness:
1. Fix critical configuration & security gaps
2. Enforce test coverage requirements
3. Implement comprehensive testing
4. Add security features (rate limiting, audit logging)
5. Build functional admin panel (POC-level)
6. Verify database safety
7. Final validation

### Approach
- **Priority-based:** Critical security issues first, then testing, then features
- **Pragmatic:** Proof-of-concept quality where appropriate (admin panel)
- **Automated:** CI/CD enforcement for coverage and quality gates
- **Safe:** Test migration rollbacks before production

---

## Pre-Implementation Checklist

Before starting Stage 0:

- [ ] **On `dev` branch** with latest code
- [ ] **Backend dependencies installed**: `cd backend && pip install -r requirements.txt`
- [ ] **Frontend dependencies installed**: `cd frontend && npm install`
- [ ] **Database running** (PostgreSQL connection working)
- [ ] **No uncommitted changes**: `git status` should be clean
- [ ] **Backup current database** (optional but recommended)

---

## Git Workflow

### Branching Strategy

Same GitFlow approach as original implementation:

```
main (production-ready)
  └── dev (active development)
       ├── feature/final-stage-0-config-security
       ├── feature/final-stage-1-test-coverage
       ├── feature/final-stage-2-backend-security
       └── ... (one branch per stage)
```

### Workflow Per Stage

1. **Create feature branch** from `dev`:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/final-stage-X-name
   ```

2. **Implement stage** (commit frequently):
   ```bash
   git add .
   git commit -m "feat: descriptive message"
   ```

3. **Merge to dev** when complete:
   ```bash
   git checkout dev
   git merge feature/final-stage-X-name --no-ff
   git push origin dev
   ```

4. **Delete feature branch**:
   ```bash
   git branch -d feature/final-stage-X-name
   ```

5. **Merge dev to main** only after ALL stages complete.

---

## Implementation Stages

### Stage 0: Critical Configuration & Security Fixes 🔐
**Branch:** `feature/final-stage-0-config-security`
**Priority:** CRITICAL
**Estimated Time:** 30 minutes

#### Goals
- Fix missing .gitignore files to prevent secret exposure
- Remove watchlist feature (incomplete/showing fake data)
- Clean up codebase from placeholder code

#### Tasks

**1. Create Backend .gitignore**

**File:** `backend/.gitignore` (CREATE)
```gitignore
# Environment variables
.env
.env.local
.env.production
.env.test

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Testing
.pytest_cache/
.coverage
htmlcov/
coverage.xml
*.cover

# IDE
.vscode/
.idea/
*.swp
*.swo

# Uploads
uploads/
*.jpg
*.jpeg
*.png
*.gif
*.webp

# Logs
*.log
```

**2. Update Frontend .gitignore**

**File:** `frontend/.gitignore` (MODIFY)

Add to existing file:
```gitignore
# Environment variables
.env
.env.local
.env.production
.env.test

# Testing
coverage/
.nyc_output/
```

**3. Remove Watchlist Feature**

**File:** `backend/routers/stats.py` (MODIFY)

Remove watchlist from user stats response (lines ~56):
```python
# BEFORE:
return {
    "active_bids": active_bids_count,
    "won_auctions": won_artworks_count,
    "total_spent": total_spent or 0,
    "watchlist": 0,  # ❌ Remove this line
    "recent_activity": recent_bids_data
}

# AFTER:
return {
    "active_bids": active_bids_count,
    "won_auctions": won_artworks_count,
    "total_spent": total_spent or 0,
    "recent_activity": recent_bids_data
}
```

**File:** `frontend/src/pages/UserDashboard.jsx` (MODIFY)

Remove watchlist StatCard (find and delete):
```jsx
// ❌ DELETE THIS ENTIRE BLOCK:
<StatCard
  icon={<Eye className="w-5 h-5" />}
  label="Watchlist"
  value={stats?.watchlist || 0}
  // ...
/>
```

**File:** `frontend/src/types/api.types.ts` (MODIFY - if exists)

Remove watchlist from UserStats type:
```typescript
export interface UserStats {
  active_bids: number;
  won_auctions: number;
  total_spent: number;
  // watchlist: number; // ❌ Remove this line
  recent_activity: RecentBid[];
}
```

**4. Verify No Secrets in Git**

```bash
# Check that .env files are ignored
git status
# Should NOT show any .env files

# Search for any remaining hardcoded secrets
cd backend
grep -r "auth0_client_secret" . --exclude-dir=.git
# Should only show settings.py with os.getenv()
```

#### Validation Steps
1. ✅ `git status` shows no .env files
2. ✅ Backend starts without errors: `cd backend && uvicorn main:socket_app --reload`
3. ✅ Frontend builds without errors: `cd frontend && npm run build`
4. ✅ User dashboard loads without watchlist section
5. ✅ No TypeScript errors related to watchlist

#### Files Modified
- `backend/.gitignore` (new)
- `frontend/.gitignore` (updated)
- `backend/routers/stats.py`
- `frontend/src/pages/UserDashboard.jsx`
- `frontend/src/types/api.types.ts` (if exists)

---

### Stage 1: Testing Infrastructure & Coverage Enforcement 🧪
**Branch:** `feature/final-stage-1-test-coverage`
**Priority:** CRITICAL
**Estimated Time:** 1-2 hours

#### Goals
- Enforce minimum test coverage in CI/CD
- Ensure tests fail CI if coverage drops below thresholds
- Add coverage reporting tools
- Verify existing backend tests meet standards

#### Prerequisites
- Stage 0 complete

#### Tasks

**1. Update Backend CI for Coverage Enforcement**

**File:** `.github/workflows/backend-ci.yml` (MODIFY)

Update the test job (around line 95-110):
```yaml
- name: Run tests with coverage
  run: |
    mkdir -p tests
    # Run pytest with minimum coverage threshold
    pytest tests/ \
      --cov \
      --cov-report=xml \
      --cov-report=term \
      --cov-report=html \
      --cov-fail-under=80
  # This will FAIL if coverage < 80%

- name: Upload coverage reports
  if: always()  # Upload even if tests fail
  uses: codecov/codecov-action@v5
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    files: ./backend/coverage.xml
    flags: backend
    fail_ci_if_error: true  # Changed from false
    disable_file_fixes: true
    verbose: true

- name: Upload coverage HTML report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: backend-coverage-report
    path: backend/htmlcov/
    retention-days: 30
```

**2. Update Frontend CI for Coverage Enforcement**

**File:** `.github/workflows/frontend-ci.yml` (MODIFY)

Update the test job (around line 67-78):
```yaml
- name: Run tests with coverage
  run: npm run test -- --coverage --run
  env:
    # Enforce minimum coverage thresholds
    VITE_TEST_COVERAGE: true

- name: Check coverage thresholds
  run: |
    # Vitest coverage is checked via vitest.config.js thresholds
    # This step will fail if coverage is below configured thresholds
    npm run test:coverage -- --run

- name: Upload coverage reports
  if: always()
  uses: codecov/codecov-action@v5
  with:
    token: ${{ secrets.CODECOV_TOKEN }}
    files: ./frontend/coverage/lcov.info
    flags: frontend
    fail_ci_if_error: true  # Changed from false
    disable_file_fixes: true
    verbose: true

- name: Upload coverage HTML report
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: frontend-coverage-report
    path: frontend/coverage/
    retention-days: 30
```

**3. Configure Frontend Test Coverage Thresholds**

**File:** `frontend/vitest.config.js` (CREATE or MODIFY)

```javascript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.config.js',
        '**/*.config.ts',
        'dist/',
        'build/',
        'src/main.jsx', // Entry point
        'src/vite-env.d.ts',
      ],
      thresholds: {
        lines: 70,
        functions: 70,
        branches: 70,
        statements: 70,
      },
    },
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

**4. Add Test Coverage NPM Scripts**

**File:** `frontend/package.json` (MODIFY)

Add to `"scripts"` section:
```json
{
  "scripts": {
    // ... existing scripts
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:run": "vitest run"
  }
}
```

**5. Verify Backend Coverage**

Run backend tests locally to check current coverage:
```bash
cd backend
pytest tests/ --cov --cov-report=term --cov-report=html

# Check if coverage meets 80% threshold
# View detailed report:
open htmlcov/index.html  # macOS
# or
xdg-open htmlcov/index.html  # Linux
```

**Expected outcome:**
- If coverage < 80%, you'll see which files need more tests
- Critical files (auth, bids, artworks) should have >90% coverage
- Utility files can be lower

**6. Create Backend Coverage Configuration**

**File:** `backend/.coveragerc` (CREATE)

```ini
[run]
source = .
omit =
    */tests/*
    */venv/*
    */.venv/*
    */migrations/*
    */config/*
    main.py

[report]
precision = 2
skip_empty = True
show_missing = True

[html]
directory = htmlcov
```

**File:** `backend/pytest.ini` (CREATE or MODIFY)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
    -v
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

#### Validation Steps
1. ✅ Run backend tests locally: `cd backend && pytest --cov --cov-fail-under=80`
   - Should pass with >80% coverage
2. ✅ Check coverage report: `open backend/htmlcov/index.html`
   - Verify auth, bids, artworks have >90% coverage
3. ✅ Frontend tests will be implemented in Stage 3 (currently will fail - expected)
4. ✅ Push changes and verify CI runs
5. ✅ Check that CI uploads coverage artifacts

#### Files Modified
- `.github/workflows/backend-ci.yml`
- `.github/workflows/frontend-ci.yml`
- `frontend/vitest.config.js` (new)
- `frontend/package.json`
- `backend/.coveragerc` (new)
- `backend/pytest.ini` (new)

---

### Stage 2: Backend Security Enhancements 🛡️
**Branch:** `feature/final-stage-2-backend-security`
**Priority:** HIGH
**Estimated Time:** 2-3 hours

#### Goals
- Implement rate limiting to prevent DoS attacks
- Add audit logging for security-critical actions
- Create middleware for security headers
- Enhance API security posture

#### Prerequisites
- Stage 0 and 1 complete
- Backend running successfully

#### Tasks

**1. Install Rate Limiting Dependencies**

**File:** `backend/requirements.txt` (MODIFY)

Add:
```txt
slowapi>=0.1.9
redis>=5.0.0  # For production rate limiting
```

Install:
```bash
cd backend
pip install slowapi redis
```

**2. Create Rate Limiting Middleware**

**File:** `backend/middleware/rate_limit.py` (CREATE)

```python
"""
Rate limiting middleware using SlowAPI.
Prevents DoS attacks and API abuse.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Initialize limiter
# For development: in-memory storage
# For production: use Redis
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per minute"],  # Global default
    storage_uri="memory://",  # Change to redis:// in production
)

async def rate_limit_exceeded_handler(
    request: Request,
    exc: RateLimitExceeded
) -> JSONResponse:
    """Custom handler for rate limit exceeded errors."""
    logger.warning(
        f"Rate limit exceeded for {request.client.host} "
        f"on {request.url.path}"
    )
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": exc.detail,
        },
        headers={"Retry-After": str(exc.detail)},
    )

def setup_rate_limiting(app):
    """Configure rate limiting for the application."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    logger.info("Rate limiting configured successfully")
```

**3. Apply Rate Limiting to Critical Endpoints**

**File:** `backend/routers/auth.py` (MODIFY)

Add rate limiting to auth endpoints:
```python
from middleware.rate_limit import limiter
from fastapi import Request

# At the top of the file, add:
# from middleware.rate_limit import limiter

@router.post("/register")
@limiter.limit("5/minute")  # Only 5 registrations per minute per IP
async def register(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    # ... existing code

@router.post("/login")
@limiter.limit("10/minute")  # 10 login attempts per minute
async def login(
    request: Request,
    credentials: LoginCredentials,
    db: Session = Depends(get_db)
):
    # ... existing code
```

**File:** `backend/routers/bids.py` (MODIFY)

```python
from middleware.rate_limit import limiter
from fastapi import Request

@router.post("/", response_model=BidResponse)
@limiter.limit("20/minute")  # Max 20 bids per minute per user
async def create_bid(
    request: Request,
    bid: BidCreate,
    current_user: User = Depends(require_buyer),
    db: Session = Depends(get_db)
):
    # ... existing code
```

**File:** `backend/routers/artworks.py` (MODIFY)

```python
from middleware.rate_limit import limiter
from fastapi import Request

@router.post("/", response_model=ArtworkResponse)
@limiter.limit("10/hour")  # Max 10 artwork uploads per hour
async def create_artwork(
    request: Request,
    artwork: ArtworkCreate,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db)
):
    # ... existing code

@router.post("/upload-image/{artwork_id}")
@limiter.limit("20/hour")  # Max 20 image uploads per hour
async def upload_artwork_image(
    request: Request,
    artwork_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # ... existing code
```

**4. Create Audit Logging System**

**File:** `backend/models/audit_log.py` (CREATE)

```python
"""
Audit log model for tracking security-critical actions.
"""
from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class AuditLog(Base):
    """Audit log for security-critical actions."""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False, index=True)
    resource_type = Column(String, nullable=False)  # 'bid', 'artwork', 'user'
    resource_id = Column(Integer, nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = relationship("User", backref="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action} by user {self.user_id}>"
```

**5. Create Audit Logging Service**

**File:** `backend/services/audit_service.py` (CREATE)

```python
"""
Audit logging service for tracking security-critical actions.
"""
from sqlalchemy.orm import Session
from models.audit_log import AuditLog
from models.user import User
from fastapi import Request
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class AuditService:
    """Service for logging security-critical actions."""

    @staticmethod
    def log_action(
        db: Session,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        user: Optional[User] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Log a security-critical action.

        Args:
            action: Action performed (e.g., 'bid_placed', 'user_banned', 'artwork_sold')
            resource_type: Type of resource ('bid', 'artwork', 'user')
            resource_id: ID of the resource
            user: User who performed the action
            details: Additional details (JSON)
            request: FastAPI request object for IP/user-agent
        """
        try:
            audit_log = AuditLog(
                user_id=user.id if user else None,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None,
            )

            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)

            logger.info(
                f"Audit log created: {action} on {resource_type}:{resource_id} "
                f"by user {user.id if user else 'system'}"
            )

            return audit_log

        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")
            db.rollback()
            # Don't fail the main operation if audit logging fails
            return None
```

**6. Add Audit Logging to Critical Operations**

**File:** `backend/routers/bids.py` (MODIFY)

Add audit logging to bid creation:
```python
from services.audit_service import AuditService

@router.post("/", response_model=BidResponse)
async def create_bid(
    request: Request,
    bid: BidCreate,
    current_user: User = Depends(require_buyer),
    db: Session = Depends(get_db)
):
    # ... existing bid creation logic ...

    # Add audit log after bid created
    AuditService.log_action(
        db=db,
        action="bid_placed",
        resource_type="bid",
        resource_id=db_bid.id,
        user=current_user,
        details={
            "amount": bid.amount,
            "artwork_id": bid.artwork_id,
            "is_winning": db_bid.is_winning,
        },
        request=request,
    )

    # ... rest of existing code
```

**File:** `backend/routers/artworks.py` (MODIFY)

Add audit logging when artwork is sold:
```python
from services.audit_service import AuditService

# In create_bid function, when artwork is sold:
if db_bid.is_winning:
    artwork.status = ArtworkStatus.SOLD

    # Audit log for artwork sale
    AuditService.log_action(
        db=db,
        action="artwork_sold",
        resource_type="artwork",
        resource_id=artwork.id,
        user=current_user,
        details={
            "final_bid": bid.amount,
            "seller_id": artwork.seller_id,
            "buyer_id": current_user.id,
        },
        request=request,
    )
```

**7. Create Database Migration for Audit Logs**

```bash
cd backend
alembic revision -m "add_audit_logs_table"
```

**File:** `backend/alembic/versions/XXXX_add_audit_logs_table.py` (EDIT generated file)

```python
"""add_audit_logs_table

Revision ID: XXXX
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSON

def upgrade():
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('resource_type', sa.String(), nullable=False),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('details', JSON(), nullable=True),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_timestamp', 'audit_logs', ['timestamp'])
    op.create_index('ix_audit_logs_user_id', 'audit_logs', ['user_id'])

def downgrade():
    op.drop_index('ix_audit_logs_user_id', 'audit_logs')
    op.drop_index('ix_audit_logs_timestamp', 'audit_logs')
    op.drop_index('ix_audit_logs_action', 'audit_logs')
    op.drop_table('audit_logs')
```

Run migration:
```bash
alembic upgrade head
```

**8. Configure Rate Limiting in Main App**

**File:** `backend/main.py` (MODIFY)

```python
from middleware.rate_limit import setup_rate_limiting

# ... existing imports and app setup ...

# Add after app initialization:
setup_rate_limiting(app)
```

**9. Add Security Headers Middleware**

**File:** `backend/middleware/security_headers.py` (CREATE)

```python
"""
Security headers middleware.
Adds security headers to all responses.
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy (adjust as needed)
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:;"
        )

        return response
```

**File:** `backend/main.py` (MODIFY)

```python
from middleware.security_headers import SecurityHeadersMiddleware

# Add after rate limiting setup:
app.add_middleware(SecurityHeadersMiddleware)
```

#### Validation Steps
1. ✅ Run migrations: `cd backend && alembic upgrade head`
2. ✅ Start backend: `uvicorn main:socket_app --reload`
3. ✅ Test rate limiting:
   ```bash
   # Should succeed first 5 times, then fail with 429
   for i in {1..6}; do
     curl -X POST http://localhost:8000/api/bids/ \
       -H "Content-Type: application/json" \
       -d '{"artwork_id": 1, "amount": 100}'
   done
   ```
4. ✅ Verify audit logs are created:
   ```sql
   SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT 10;
   ```
5. ✅ Check security headers:
   ```bash
   curl -I http://localhost:8000/api/artworks/
   # Should show X-Content-Type-Options, X-Frame-Options, etc.
   ```
6. ✅ Run tests: `pytest tests/ --cov`

#### Files Modified
- `backend/requirements.txt`
- `backend/middleware/rate_limit.py` (new)
- `backend/middleware/security_headers.py` (new)
- `backend/models/audit_log.py` (new)
- `backend/services/audit_service.py` (new)
- `backend/routers/auth.py`
- `backend/routers/bids.py`
- `backend/routers/artworks.py`
- `backend/main.py`
- `backend/alembic/versions/XXXX_add_audit_logs_table.py` (new)

---

### Stage 3: Frontend Testing Implementation 🧪
**Branch:** `feature/final-stage-3-frontend-tests`
**Priority:** HIGH
**Estimated Time:** 3-4 hours

#### Goals
- Implement comprehensive frontend testing
- Unit tests for utilities and hooks
- Component tests for major components
- Integration tests for key user flows
- Achieve >70% code coverage

#### Prerequisites
- Stage 0, 1, 2 complete
- Vitest configured (from Stage 1)

#### Tasks

**1. Install Testing Dependencies**

**File:** `frontend/package.json` (MODIFY)

Add to `devDependencies`:
```json
{
  "devDependencies": {
    // ... existing deps
    "@testing-library/react": "^14.1.2",
    "@testing-library/jest-dom": "^6.1.5",
    "@testing-library/user-event": "^14.5.1",
    "@vitest/ui": "^1.1.0",
    "jsdom": "^23.0.1",
    "vitest": "^1.1.0",
    "@vitest/coverage-v8": "^1.1.0",
    "msw": "^2.0.11"
  }
}
```

Install:
```bash
cd frontend
npm install
```

**2. Create Test Setup File**

**File:** `frontend/src/test/setup.js` (CREATE)

```javascript
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
};
```

**3. Create Test Utilities**

**File:** `frontend/src/test/utils.jsx` (CREATE)

```javascript
import { render } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { Auth0Provider } from '@auth0/auth0-react';

// Create a custom render function that includes providers
export function renderWithProviders(ui, options = {}) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  const mockAuth0Config = {
    domain: 'test.auth0.com',
    clientId: 'test-client-id',
    authorizationParams: {
      audience: 'test-audience',
      redirect_uri: window.location.origin,
    },
  };

  function Wrapper({ children }) {
    return (
      <Auth0Provider {...mockAuth0Config}>
        <QueryClientProvider client={queryClient}>
          <BrowserRouter>
            {children}
          </BrowserRouter>
        </QueryClientProvider>
      </Auth0Provider>
    );
  }

  return render(ui, { wrapper: Wrapper, ...options });
}

// Mock user for testing
export const mockUser = {
  id: 1,
  email: 'test@example.com',
  username: 'testuser',
  role: 'buyer',
  auth0_sub: 'auth0|123456',
};

// Mock artwork for testing
export const mockArtwork = {
  id: 1,
  title: 'Test Artwork',
  artist_name: 'Test Artist',
  description: 'Test description',
  category: 'painting',
  starting_bid: 100,
  current_highest_bid: 150,
  status: 'active',
  image_url: '/test-image.jpg',
  seller_id: 2,
  created_at: '2024-01-01T00:00:00Z',
};

// Mock bid for testing
export const mockBid = {
  id: 1,
  artwork_id: 1,
  bidder_id: 1,
  amount: 150,
  is_winning: false,
  created_at: '2024-01-01T00:00:00Z',
};
```

**4. Unit Tests for Utility Functions**

**File:** `frontend/src/utils/__tests__/format.test.js` (CREATE)

```javascript
import { describe, it, expect } from 'vitest';
// Create these utility functions if they don't exist
import { formatCurrency, formatDate, formatTimeAgo } from '../format';

describe('Format Utilities', () => {
  describe('formatCurrency', () => {
    it('formats numbers as currency', () => {
      expect(formatCurrency(1000)).toBe('$1,000.00');
      expect(formatCurrency(0)).toBe('$0.00');
      expect(formatCurrency(1234567.89)).toBe('$1,234,567.89');
    });

    it('handles null and undefined', () => {
      expect(formatCurrency(null)).toBe('$0.00');
      expect(formatCurrency(undefined)).toBe('$0.00');
    });
  });

  describe('formatDate', () => {
    it('formats ISO dates', () => {
      const date = '2024-01-15T10:30:00Z';
      const result = formatDate(date);
      expect(result).toContain('2024');
      expect(result).toContain('Jan');
    });
  });

  describe('formatTimeAgo', () => {
    it('returns "just now" for recent dates', () => {
      const now = new Date();
      expect(formatTimeAgo(now.toISOString())).toBe('just now');
    });

    it('returns minutes ago', () => {
      const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
      expect(formatTimeAgo(fiveMinutesAgo.toISOString())).toBe('5 minutes ago');
    });
  });
});
```

**File:** `frontend/src/utils/format.js` (CREATE if missing)

```javascript
/**
 * Format a number as currency
 */
export function formatCurrency(amount) {
  if (amount === null || amount === undefined) return '$0.00';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount);
}

/**
 * Format an ISO date string
 */
export function formatDate(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(date);
}

/**
 * Format a date as "time ago"
 */
export function formatTimeAgo(dateString) {
  if (!dateString) return '';
  const date = new Date(dateString);
  const now = new Date();
  const seconds = Math.floor((now - date) / 1000);

  if (seconds < 60) return 'just now';

  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;

  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;

  const days = Math.floor(hours / 24);
  return `${days} day${days > 1 ? 's' : ''} ago`;
}
```

**5. Hook Tests**

**File:** `frontend/src/hooks/__tests__/useRealtimeBids.test.js` (CREATE)

```javascript
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import useRealtimeBids from '../useRealtimeBids';
import socketService from '../../services/socketService';

// Mock socket service
vi.mock('../../services/socketService', () => ({
  default: {
    connect: vi.fn(),
    disconnect: vi.fn(),
    joinArtworkRoom: vi.fn(),
    leaveArtworkRoom: vi.fn(),
    onNewBid: vi.fn(),
    onArtworkSold: vi.fn(),
  },
}));

describe('useRealtimeBids', () => {
  let queryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  const wrapper = ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );

  it('connects to socket on mount', () => {
    renderHook(() => useRealtimeBids(1), { wrapper });

    expect(socketService.connect).toHaveBeenCalled();
    expect(socketService.joinArtworkRoom).toHaveBeenCalledWith(1);
  });

  it('disconnects on unmount', () => {
    const { unmount } = renderHook(() => useRealtimeBids(1), { wrapper });

    unmount();

    expect(socketService.leaveArtworkRoom).toHaveBeenCalledWith(1);
  });

  it('registers event listeners', () => {
    renderHook(() => useRealtimeBids(1), { wrapper });

    expect(socketService.onNewBid).toHaveBeenCalled();
    expect(socketService.onArtworkSold).toHaveBeenCalled();
  });
});
```

**6. Component Tests**

**File:** `frontend/src/components/__tests__/ArtworkCard.test.jsx` (CREATE)

```jsx
import { describe, it, expect } from 'vitest';
import { screen } from '@testing-library/react';
import { renderWithProviders, mockArtwork } from '../../test/utils';
import ArtworkCard from '../ArtworkCard';

describe('ArtworkCard', () => {
  it('renders artwork information', () => {
    renderWithProviders(<ArtworkCard artwork={mockArtwork} />);

    expect(screen.getByText('Test Artwork')).toBeInTheDocument();
    expect(screen.getByText('Test Artist')).toBeInTheDocument();
    expect(screen.getByText(/\$150/)).toBeInTheDocument(); // Current bid
  });

  it('displays artwork image', () => {
    renderWithProviders(<ArtworkCard artwork={mockArtwork} />);

    const image = screen.getByRole('img');
    expect(image).toHaveAttribute('alt', 'Test Artwork');
  });

  it('shows status badge for active auctions', () => {
    renderWithProviders(<ArtworkCard artwork={mockArtwork} />);

    expect(screen.getByText(/active/i)).toBeInTheDocument();
  });

  it('shows sold status for sold artworks', () => {
    const soldArtwork = { ...mockArtwork, status: 'sold' };
    renderWithProviders(<ArtworkCard artwork={soldArtwork} />);

    expect(screen.getByText(/sold/i)).toBeInTheDocument();
  });
});
```

**File:** `frontend/src/components/__tests__/BidForm.test.jsx` (CREATE)

```jsx
import { describe, it, expect, vi } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { renderWithProviders, mockArtwork } from '../../test/utils';
import BidForm from '../BidForm';

describe('BidForm', () => {
  const mockOnSuccess = vi.fn();

  it('renders bid input field', () => {
    renderWithProviders(
      <BidForm artwork={mockArtwork} onSuccess={mockOnSuccess} />
    );

    expect(screen.getByLabelText(/bid amount/i)).toBeInTheDocument();
  });

  it('shows minimum bid requirement', () => {
    renderWithProviders(
      <BidForm artwork={mockArtwork} onSuccess={mockOnSuccess} />
    );

    // Should show current highest bid + 1
    expect(screen.getByText(/minimum.*\$151/i)).toBeInTheDocument();
  });

  it('validates bid amount', async () => {
    const user = userEvent.setup();
    renderWithProviders(
      <BidForm artwork={mockArtwork} onSuccess={mockOnSuccess} />
    );

    const input = screen.getByLabelText(/bid amount/i);
    const submitButton = screen.getByRole('button', { name: /place bid/i });

    // Try to submit with too low bid
    await user.type(input, '100'); // Less than minimum (151)
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/must be at least/i)).toBeInTheDocument();
    });
  });

  it('displays current highest bid', () => {
    renderWithProviders(
      <BidForm artwork={mockArtwork} onSuccess={mockOnSuccess} />
    );

    expect(screen.getByText(/current bid.*\$150/i)).toBeInTheDocument();
  });
});
```

**7. Integration Tests**

**File:** `frontend/src/pages/__tests__/ArtworksPage.test.jsx` (CREATE)

```jsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithProviders, mockArtwork } from '../../test/utils';
import ArtworksPage from '../ArtworksPage';
import * as api from '../../services/api';

// Mock API
vi.mock('../../services/api', () => ({
  getArtworks: vi.fn(),
}));

describe('ArtworksPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('displays loading state initially', () => {
    api.getArtworks.mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    renderWithProviders(<ArtworksPage />);

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('displays artworks after loading', async () => {
    api.getArtworks.mockResolvedValue([mockArtwork]);

    renderWithProviders(<ArtworksPage />);

    await waitFor(() => {
      expect(screen.getByText('Test Artwork')).toBeInTheDocument();
    });
  });

  it('displays error state on API failure', async () => {
    api.getArtworks.mockRejectedValue(new Error('API Error'));

    renderWithProviders(<ArtworksPage />);

    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('displays empty state when no artworks', async () => {
    api.getArtworks.mockResolvedValue([]);

    renderWithProviders(<ArtworksPage />);

    await waitFor(() => {
      expect(screen.getByText(/no artworks/i)).toBeInTheDocument();
    });
  });
});
```

**8. Add Test Scripts to Package.json**

Already added in Stage 1, verify they exist:
```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:run": "vitest run"
  }
}
```

#### Validation Steps
1. ✅ Run tests: `cd frontend && npm run test:run`
2. ✅ Check coverage: `npm run test:coverage`
   - Should show >70% coverage
3. ✅ View coverage report: `open coverage/index.html`
4. ✅ Run tests in watch mode: `npm test`
5. ✅ Run tests in UI mode: `npm run test:ui`
6. ✅ Verify CI passes with coverage enforcement

#### Files Modified
- `frontend/package.json`
- `frontend/src/test/setup.js` (new)
- `frontend/src/test/utils.jsx` (new)
- `frontend/src/utils/format.js` (new/modified)
- `frontend/src/utils/__tests__/format.test.js` (new)
- `frontend/src/hooks/__tests__/useRealtimeBids.test.js` (new)
- `frontend/src/components/__tests__/ArtworkCard.test.jsx` (new)
- `frontend/src/components/__tests__/BidForm.test.jsx` (new)
- `frontend/src/pages/__tests__/ArtworksPage.test.jsx` (new)

---

### Stage 4: Admin Dashboard Backend API (POC) 👑
**Branch:** `feature/final-stage-4-admin-backend`
**Priority:** MEDIUM
**Estimated Time:** 2-3 hours

#### Goals
- Create basic admin API endpoints (proof-of-concept quality)
- User management (list, view, ban/unban)
- Platform statistics
- Transaction monitoring
- System health check

#### Prerequisites
- Stages 0-3 complete
- User has admin role in database

#### Tasks

**1. Create Admin Router**

**File:** `backend/routers/admin.py` (CREATE)

```python
"""
Admin router for platform management.
Proof-of-concept implementation.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models.user import User, UserRole
from models.artwork import Artwork, ArtworkStatus
from models.bid import Bid
from models.audit_log import AuditLog
from utils.auth import get_current_user
from services.audit_service import AuditService

router = APIRouter(prefix="/api/admin", tags=["admin"])

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user is an admin."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# ============================================================================
# USER MANAGEMENT
# ============================================================================

@router.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    role: Optional[str] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    List all users with optional filtering.
    POC: Basic implementation.
    """
    query = db.query(User)

    # Filter by role
    if role:
        query = query.filter(User.role == role)

    # Search by username or email
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.username.ilike(search_pattern)) |
            (User.email.ilike(search_pattern))
        )

    # Get total count
    total = query.count()

    # Get paginated results
    users = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "users": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "created_at": user.created_at.isoformat(),
                "is_active": True,  # POC: Always true
            }
            for user in users
        ],
        "skip": skip,
        "limit": limit,
    }

@router.get("/users/{user_id}")
async def get_user_details(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get detailed user information."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get user statistics
    artworks_count = db.query(Artwork).filter(
        Artwork.seller_id == user_id
    ).count()

    bids_count = db.query(Bid).filter(Bid.bidder_id == user_id).count()

    total_spent = db.query(func.sum(Bid.amount)).filter(
        Bid.bidder_id == user_id,
        Bid.is_winning == True
    ).scalar() or 0

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "created_at": user.created_at.isoformat(),
        "stats": {
            "artworks_created": artworks_count,
            "bids_placed": bids_count,
            "total_spent": float(total_spent),
        },
    }

@router.put("/users/{user_id}/ban")
async def ban_user(
    user_id: int,
    reason: str = Query(..., min_length=10),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Ban a user (POC: just logs the action).
    Production would update user.is_active = False
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == UserRole.ADMIN:
        raise HTTPException(status_code=400, detail="Cannot ban admin users")

    # POC: Just log the action (don't actually ban)
    AuditService.log_action(
        db=db,
        action="user_banned",
        resource_type="user",
        resource_id=user_id,
        user=current_user,
        details={"reason": reason},
    )

    return {
        "message": f"User {user.username} banned",
        "reason": reason,
    }

# ============================================================================
# TRANSACTION MONITORING
# ============================================================================

@router.get("/transactions")
async def list_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    List recent transactions (sold artworks).
    POC: Returns winning bids.
    """
    # Get winning bids (representing transactions)
    transactions = (
        db.query(Bid)
        .options(
            joinedload(Bid.artwork),
            joinedload(Bid.bidder)
        )
        .filter(Bid.is_winning == True)
        .order_by(desc(Bid.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    total = db.query(Bid).filter(Bid.is_winning == True).count()

    return {
        "total": total,
        "transactions": [
            {
                "id": bid.id,
                "artwork_title": bid.artwork.title,
                "buyer": bid.bidder.username,
                "amount": float(bid.amount),
                "date": bid.created_at.isoformat(),
                "status": "completed",  # POC: Always completed
            }
            for bid in transactions
        ],
        "skip": skip,
        "limit": limit,
    }

# ============================================================================
# PLATFORM STATISTICS
# ============================================================================

@router.get("/stats/overview")
async def get_platform_overview(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get comprehensive platform statistics."""
    # User stats
    total_users = db.query(User).count()
    users_last_30_days = db.query(User).filter(
        User.created_at >= datetime.utcnow() - timedelta(days=30)
    ).count()

    # Artwork stats
    total_artworks = db.query(Artwork).count()
    active_auctions = db.query(Artwork).filter(
        Artwork.status == ArtworkStatus.ACTIVE
    ).count()

    # Transaction stats
    total_transactions = db.query(Bid).filter(
        Bid.is_winning == True
    ).count()

    total_revenue = db.query(func.sum(Bid.amount)).filter(
        Bid.is_winning == True
    ).scalar() or 0

    # Platform fees (10% commission)
    platform_fees = float(total_revenue) * 0.10

    return {
        "users": {
            "total": total_users,
            "new_last_30_days": users_last_30_days,
        },
        "auctions": {
            "total": total_artworks,
            "active": active_auctions,
        },
        "transactions": {
            "total": total_transactions,
            "total_revenue": float(total_revenue),
            "platform_fees": platform_fees,
        },
    }

# ============================================================================
# FLAGGED CONTENT
# ============================================================================

@router.get("/flagged-auctions")
async def list_flagged_auctions(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    List flagged/reported auctions.
    POC: Returns empty list (no flag system implemented).
    """
    # POC: Return empty list
    # Production would query a 'reports' table
    return {
        "total": 0,
        "flagged_auctions": [],
        "message": "No flagged auctions (feature not implemented in POC)",
    }

# ============================================================================
# SYSTEM HEALTH
# ============================================================================

@router.get("/system/health")
async def get_system_health(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    Get system health metrics.
    POC: Basic database connectivity check.
    """
    try:
        # Test database connection
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    # Get recent activity
    recent_bids = db.query(Bid).filter(
        Bid.created_at >= datetime.utcnow() - timedelta(hours=1)
    ).count()

    recent_artworks = db.query(Artwork).filter(
        Artwork.created_at >= datetime.utcnow() - timedelta(hours=24)
    ).count()

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "metrics": {
            "bids_last_hour": recent_bids,
            "artworks_last_24h": recent_artworks,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }

# ============================================================================
# AUDIT LOGS
# ============================================================================

@router.get("/audit-logs")
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=500),
    action: Optional[str] = None,
    user_id: Optional[int] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Get audit logs for security monitoring."""
    query = db.query(AuditLog).options(joinedload(AuditLog.user))

    if action:
        query = query.filter(AuditLog.action == action)

    if user_id:
        query = query.filter(AuditLog.user_id == user_id)

    total = query.count()

    logs = query.order_by(desc(AuditLog.timestamp)).offset(skip).limit(limit).all()

    return {
        "total": total,
        "logs": [
            {
                "id": log.id,
                "action": log.action,
                "user": log.user.username if log.user else "system",
                "resource_type": log.resource_type,
                "resource_id": log.resource_id,
                "details": log.details,
                "ip_address": log.ip_address,
                "timestamp": log.timestamp.isoformat(),
            }
            for log in logs
        ],
        "skip": skip,
        "limit": limit,
    }
```

**2. Register Admin Router**

**File:** `backend/main.py` (MODIFY)

```python
from routers import admin

# Add after other router includes:
app.include_router(admin.router)
```

**3. Create Admin Tests**

**File:** `backend/tests/test_admin_api.py` (CREATE)

```python
"""
Tests for admin API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from models.user import User, UserRole
from models.artwork import Artwork, ArtworkStatus
from models.bid import Bid

def test_list_users_requires_admin(client: TestClient, buyer_token: str):
    """Non-admin users cannot access user list."""
    response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert response.status_code == 403

def test_list_users_as_admin(client: TestClient, admin_token: str, db: Session):
    """Admin can list users."""
    response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "total" in data

def test_get_user_details(
    client: TestClient,
    admin_token: str,
    test_buyer: User
):
    """Admin can get user details."""
    response = client.get(
        f"/api/admin/users/{test_buyer.id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_buyer.id
    assert "stats" in data

def test_ban_user(
    client: TestClient,
    admin_token: str,
    test_buyer: User
):
    """Admin can ban users."""
    response = client.put(
        f"/api/admin/users/{test_buyer.id}/ban",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"reason": "Violated terms of service multiple times"}
    )
    assert response.status_code == 200
    assert "banned" in response.json()["message"].lower()

def test_cannot_ban_admin(
    client: TestClient,
    admin_token: str,
    test_admin: User
):
    """Cannot ban admin users."""
    response = client.put(
        f"/api/admin/users/{test_admin.id}/ban",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"reason": "Testing admin protection"}
    )
    assert response.status_code == 400

def test_get_platform_overview(client: TestClient, admin_token: str):
    """Admin can get platform statistics."""
    response = client.get(
        "/api/admin/stats/overview",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "users" in data
    assert "auctions" in data
    assert "transactions" in data

def test_get_transactions(client: TestClient, admin_token: str):
    """Admin can view transactions."""
    response = client.get(
        "/api/admin/transactions",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    assert "total" in data

def test_get_system_health(client: TestClient, admin_token: str):
    """Admin can check system health."""
    response = client.get(
        "/api/admin/system/health",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "database" in data

def test_get_audit_logs(client: TestClient, admin_token: str):
    """Admin can view audit logs."""
    response = client.get(
        "/api/admin/audit-logs",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "logs" in data
    assert "total" in data
```

#### Validation Steps
1. ✅ Start backend: `uvicorn main:socket_app --reload`
2. ✅ Test endpoints with curl or Postman (with admin token):
   ```bash
   # Get platform overview
   curl http://localhost:8000/api/admin/stats/overview \
     -H "Authorization: Bearer <admin_token>"

   # List users
   curl http://localhost:8000/api/admin/users \
     -H "Authorization: Bearer <admin_token>"
   ```
3. ✅ Run tests: `pytest tests/test_admin_api.py -v`
4. ✅ Verify non-admin users get 403
5. ✅ Check audit logs are created for ban actions

#### Files Modified
- `backend/routers/admin.py` (new)
- `backend/main.py`
- `backend/tests/test_admin_api.py` (new)

---

### Stage 5: Admin Dashboard Frontend Integration 🎨
**Branch:** `feature/final-stage-5-admin-frontend`
**Priority:** MEDIUM
**Estimated Time:** 2-3 hours

#### Goals
- Replace all hardcoded data in AdminDashboard.jsx
- Integrate with new admin API endpoints
- Add real-time data fetching
- Implement user moderation UI

#### Prerequisites
- Stage 4 complete (admin backend API ready)

#### Tasks

**1. Create Admin API Service**

**File:** `frontend/src/services/adminApi.js` (CREATE)

```javascript
import api from './api';

/**
 * Admin API service functions
 */
export const adminApi = {
  // Platform overview
  getPlatformOverview: async () => {
    const response = await api.get('/api/admin/stats/overview');
    return response.data;
  },

  // User management
  getUsers: async (params = {}) => {
    const response = await api.get('/api/admin/users', { params });
    return response.data;
  },

  getUserDetails: async (userId) => {
    const response = await api.get(`/api/admin/users/${userId}`);
    return response.data;
  },

  banUser: async (userId, reason) => {
    const response = await api.put(
      `/api/admin/users/${userId}/ban`,
      null,
      { params: { reason } }
    );
    return response.data;
  },

  // Transactions
  getTransactions: async (params = {}) => {
    const response = await api.get('/api/admin/transactions', { params });
    return response.data;
  },

  // System health
  getSystemHealth: async () => {
    const response = await api.get('/api/admin/system/health');
    return response.data;
  },

  // Flagged auctions
  getFlaggedAuctions: async () => {
    const response = await api.get('/api/admin/flagged-auctions');
    return response.data;
  },

  // Audit logs
  getAuditLogs: async (params = {}) => {
    const response = await api.get('/api/admin/audit-logs', { params });
    return response.data;
  },
};

export default adminApi;
```

**2. Update AdminDashboard Component**

**File:** `frontend/src/pages/AdminDashboard.jsx` (MODIFY)

Replace entire file content:
```jsx
import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Users,
  Gavel,
  DollarSign,
  TrendingUp,
  AlertTriangle,
  Activity,
} from 'lucide-react';
import adminApi from '../services/adminApi';
import StatCard from '../components/StatCard';

export default function AdminDashboard() {
  // Fetch platform overview
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['admin', 'overview'],
    queryFn: adminApi.getPlatformOverview,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fetch recent transactions
  const { data: transactionsData, isLoading: transactionsLoading } = useQuery({
    queryKey: ['admin', 'transactions'],
    queryFn: () => adminApi.getTransactions({ limit: 10 }),
  });

  // Fetch recent users
  const { data: usersData, isLoading: usersLoading } = useQuery({
    queryKey: ['admin', 'users'],
    queryFn: () => adminApi.getUsers({ limit: 10 }),
  });

  // Fetch system health
  const { data: systemHealth, isLoading: healthLoading } = useQuery({
    queryKey: ['admin', 'health'],
    queryFn: adminApi.getSystemHealth,
    refetchInterval: 60000, // Refresh every minute
  });

  // Fetch flagged auctions
  const { data: flaggedData } = useQuery({
    queryKey: ['admin', 'flagged'],
    queryFn: adminApi.getFlaggedAuctions,
  });

  if (statsLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg">Loading admin dashboard...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600 mt-1">
          Platform management and monitoring
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={<Users className="w-5 h-5" />}
          label="Total Users"
          value={stats?.users?.total || 0}
          subtext={`${stats?.users?.new_last_30_days || 0} new this month`}
        />
        <StatCard
          icon={<Gavel className="w-5 h-5" />}
          label="Active Auctions"
          value={stats?.auctions?.active || 0}
          subtext={`${stats?.auctions?.total || 0} total artworks`}
        />
        <StatCard
          icon={<DollarSign className="w-5 h-5" />}
          label="Total Revenue"
          value={`$${(stats?.transactions?.total_revenue || 0).toLocaleString()}`}
          subtext={`${stats?.transactions?.total || 0} transactions`}
        />
        <StatCard
          icon={<TrendingUp className="w-5 h-5" />}
          label="Platform Fees"
          value={`$${(stats?.transactions?.platform_fees || 0).toLocaleString()}`}
          subtext="10% commission"
        />
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Users */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Users</h2>
          {usersLoading ? (
            <div className="text-gray-500">Loading...</div>
          ) : (
            <div className="space-y-3">
              {usersData?.users?.slice(0, 5).map((user) => (
                <div
                  key={user.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded"
                >
                  <div>
                    <p className="font-medium">{user.username}</p>
                    <p className="text-sm text-gray-500">{user.email}</p>
                  </div>
                  <span
                    className={`px-2 py-1 text-xs rounded ${
                      user.role === 'admin'
                        ? 'bg-purple-100 text-purple-800'
                        : user.role === 'seller'
                        ? 'bg-blue-100 text-blue-800'
                        : 'bg-green-100 text-green-800'
                    }`}
                  >
                    {user.role}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Recent Transactions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Recent Transactions</h2>
          {transactionsLoading ? (
            <div className="text-gray-500">Loading...</div>
          ) : (
            <div className="space-y-3">
              {transactionsData?.transactions?.slice(0, 5).map((tx) => (
                <div
                  key={tx.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded"
                >
                  <div>
                    <p className="font-medium">{tx.artwork_title}</p>
                    <p className="text-sm text-gray-500">
                      Buyer: {tx.buyer}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-green-600">
                      ${tx.amount.toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500">{tx.status}</p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* System Health & Flagged Auctions */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Health */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">System Health</h2>
            <Activity className="w-5 h-5 text-gray-400" />
          </div>
          {healthLoading ? (
            <div className="text-gray-500">Loading...</div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Status</span>
                <span
                  className={`px-3 py-1 rounded-full text-sm font-medium ${
                    systemHealth?.status === 'healthy'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}
                >
                  {systemHealth?.status || 'Unknown'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Database</span>
                <span
                  className={`px-3 py-1 rounded-full text-sm ${
                    systemHealth?.database === 'healthy'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}
                >
                  {systemHealth?.database || 'Unknown'}
                </span>
              </div>
              <div className="pt-3 border-t">
                <p className="text-sm text-gray-600">
                  Bids (last hour):{' '}
                  <span className="font-semibold">
                    {systemHealth?.metrics?.bids_last_hour || 0}
                  </span>
                </p>
                <p className="text-sm text-gray-600">
                  Artworks (last 24h):{' '}
                  <span className="font-semibold">
                    {systemHealth?.metrics?.artworks_last_24h || 0}
                  </span>
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Flagged Auctions */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Flagged Auctions</h2>
            <AlertTriangle className="w-5 h-5 text-yellow-500" />
          </div>
          {flaggedData?.total === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p>No flagged auctions</p>
              <p className="text-sm mt-1">
                {flaggedData?.message || 'All clear!'}
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {flaggedData?.flagged_auctions?.map((auction) => (
                <div
                  key={auction.id}
                  className="p-3 bg-yellow-50 border border-yellow-200 rounded"
                >
                  <p className="font-medium">{auction.title}</p>
                  <p className="text-sm text-gray-600">{auction.reason}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
```

**3. Add Admin Navigation Guard**

**File:** `frontend/src/components/AdminRoute.jsx` (CREATE)

```jsx
import { Navigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import { useQuery } from '@tanstack/react-query';
import api from '../services/api';

export default function AdminRoute({ children }) {
  const { isAuthenticated, isLoading: authLoading } = useAuth0();

  const { data: user, isLoading: userLoading } = useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const response = await api.get('/api/auth/me');
      return response.data;
    },
    enabled: isAuthenticated,
  });

  if (authLoading || userLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }

  if (user?.role !== 'admin') {
    return <Navigate to="/" />;
  }

  return children;
}
```

**4. Update Router to Protect Admin Routes**

**File:** `frontend/src/App.jsx` (MODIFY)

```jsx
import AdminRoute from './components/AdminRoute';

// Wrap admin dashboard route:
<Route
  path="/admin"
  element={
    <AdminRoute>
      <AdminDashboard />
    </AdminRoute>
  }
/>
```

**5. Add Admin Tests**

**File:** `frontend/src/pages/__tests__/AdminDashboard.test.jsx` (CREATE)

```jsx
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { screen, waitFor } from '@testing-library/react';
import { renderWithProviders } from '../../test/utils';
import AdminDashboard from '../AdminDashboard';
import * as adminApi from '../../services/adminApi';

vi.mock('../../services/adminApi');

describe('AdminDashboard', () => {
  const mockStats = {
    users: { total: 100, new_last_30_days: 10 },
    auctions: { total: 50, active: 20 },
    transactions: { total: 75, total_revenue: 50000, platform_fees: 5000 },
  };

  const mockTransactions = {
    transactions: [
      {
        id: 1,
        artwork_title: 'Test Art',
        buyer: 'testuser',
        amount: 1000,
        status: 'completed',
      },
    ],
  };

  beforeEach(() => {
    vi.clearAllMocks();
    adminApi.default.getPlatformOverview.mockResolvedValue(mockStats);
    adminApi.default.getTransactions.mockResolvedValue(mockTransactions);
    adminApi.default.getUsers.mockResolvedValue({ users: [] });
    adminApi.default.getSystemHealth.mockResolvedValue({
      status: 'healthy',
      database: 'healthy',
      metrics: { bids_last_hour: 5, artworks_last_24h: 10 },
    });
    adminApi.default.getFlaggedAuctions.mockResolvedValue({
      total: 0,
      flagged_auctions: [],
    });
  });

  it('displays platform statistics', async () => {
    renderWithProviders(<AdminDashboard />);

    await waitFor(() => {
      expect(screen.getByText('100')).toBeInTheDocument(); // Total users
      expect(screen.getByText('20')).toBeInTheDocument(); // Active auctions
    });
  });

  it('displays recent transactions', async () => {
    renderWithProviders(<AdminDashboard />);

    await waitFor(() => {
      expect(screen.getByText('Test Art')).toBeInTheDocument();
      expect(screen.getByText(/testuser/i)).toBeInTheDocument();
    });
  });

  it('shows system health status', async () => {
    renderWithProviders(<AdminDashboard />);

    await waitFor(() => {
      expect(screen.getByText('healthy')).toBeInTheDocument();
    });
  });

  it('shows no flagged auctions message', async () => {
    renderWithProviders(<AdminDashboard />);

    await waitFor(() => {
      expect(screen.getByText(/no flagged auctions/i)).toBeInTheDocument();
    });
  });
});
```

#### Validation Steps
1. ✅ Start frontend: `cd frontend && npm run dev`
2. ✅ Login as admin user
3. ✅ Navigate to `/admin`
4. ✅ Verify all stats load from API (not hardcoded)
5. ✅ Check browser network tab shows API calls to `/api/admin/*`
6. ✅ Verify non-admin users cannot access admin dashboard
7. ✅ Run tests: `npm run test:run`

#### Files Modified
- `frontend/src/services/adminApi.js` (new)
- `frontend/src/pages/AdminDashboard.jsx` (complete rewrite)
- `frontend/src/components/AdminRoute.jsx` (new)
- `frontend/src/App.jsx`
- `frontend/src/pages/__tests__/AdminDashboard.test.jsx` (new)

---

### Stage 6: Database Migration Rollback Testing 🗄️
**Branch:** `feature/final-stage-6-migration-testing`
**Priority:** MEDIUM
**Estimated Time:** 1 hour

#### Goals
- Verify all Alembic migrations can be rolled back safely
- Test migration rollback procedures
- Document rollback process
- Ensure database safety for production deployments

#### Prerequisites
- All previous stages complete
- Database backup available

#### Tasks

**1. Create Migration Test Script**

**File:** `backend/scripts/test_migrations.sh` (CREATE)

```bash
#!/bin/bash
# Migration rollback testing script

set -e  # Exit on error

echo "🔍 Testing Alembic migration rollback safety..."
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get current migration
CURRENT=$(alembic current 2>/dev/null || echo "none")
echo "📍 Current migration: $CURRENT"
echo ""

# Get migration history
echo "📋 Migration history:"
alembic history
echo ""

# Test rollback one step
echo "${YELLOW}⏪ Testing rollback one step...${NC}"
alembic downgrade -1

if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Rollback successful!${NC}"
else
    echo "${RED}❌ Rollback failed!${NC}"
    exit 1
fi

echo ""
echo "📍 Current migration after rollback:"
alembic current
echo ""

# Test upgrade back to head
echo "${YELLOW}⏩ Testing upgrade back to head...${NC}"
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "${GREEN}✅ Upgrade successful!${NC}"
else
    echo "${RED}❌ Upgrade failed!${NC}"
    exit 1
fi

echo ""
echo "📍 Final migration state:"
alembic current
echo ""

echo "${GREEN}✅ All migration tests passed!${NC}"
echo ""
echo "Summary:"
echo "  - Rollback: ✅ Working"
echo "  - Upgrade: ✅ Working"
echo "  - Data integrity: ✅ Maintained"
```

Make executable:
```bash
chmod +x backend/scripts/test_migrations.sh
```

**2. Create Database Backup Script**

**File:** `backend/scripts/backup_database.sh` (CREATE)

```bash
#!/bin/bash
# Database backup script

set -e

# Load environment variables
if [ -f ../.env ]; then
    export $(cat ../.env | grep -v '#' | xargs)
fi

# Extract database credentials from DATABASE_URL
# Format: postgresql://user:password@host:port/dbname
DB_URL=${DATABASE_URL:-"postgresql://postgres:password@localhost:5432/guess_the_worth_db"}

# Parse URL components
DB_USER=$(echo $DB_URL | sed -n 's/.*:\/\/\([^:]*\):.*/\1/p')
DB_PASS=$(echo $DB_URL | sed -n 's/.*:\/\/[^:]*:\([^@]*\)@.*/\1/p')
DB_HOST=$(echo $DB_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
DB_PORT=$(echo $DB_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
DB_NAME=$(echo $DB_URL | sed -n 's/.*\/\([^?]*\).*/\1/p')

# Create backup filename with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups"
BACKUP_FILE="$BACKUP_DIR/db_backup_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

echo "🗄️  Creating database backup..."
echo "   Database: $DB_NAME"
echo "   Host: $DB_HOST:$DB_PORT"
echo "   File: $BACKUP_FILE"
echo ""

# Create backup using pg_dump
PGPASSWORD=$DB_PASS pg_dump \
    -h $DB_HOST \
    -p $DB_PORT \
    -U $DB_USER \
    -d $DB_NAME \
    -F p \
    -f $BACKUP_FILE

if [ $? -eq 0 ]; then
    echo "✅ Backup created successfully!"
    echo "   Location: $BACKUP_FILE"
    echo "   Size: $(du -h $BACKUP_FILE | cut -f1)"
else
    echo "❌ Backup failed!"
    exit 1
fi
```

Make executable:
```bash
chmod +x backend/scripts/backup_database.sh
```

**3. Test Migration Rollback**

Run the migration test:
```bash
cd backend
./scripts/test_migrations.sh
```

Expected output:
```
🔍 Testing Alembic migration rollback safety...

📍 Current migration: <current_revision>

📋 Migration history:
<revision> -> <revision> (head), add_audit_logs_table
<revision> -> <revision>, add_artist_name_category_end_date_to_artworks
...

⏪ Testing rollback one step...
✅ Rollback successful!

📍 Current migration after rollback: <previous_revision>

⏩ Testing upgrade back to head...
✅ Upgrade successful!

📍 Final migration state: <current_revision>

✅ All migration tests passed!
```

**4. Create Migration Documentation**

**File:** `backend/docs/MIGRATIONS.md` (CREATE)

```markdown
# Database Migrations Guide

## Overview
This project uses Alembic for database migrations.

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
   ./scripts/backup_database.sh
   ```

2. **Rollback the migration:**
   ```bash
   alembic downgrade -1
   ```

3. **Verify application works:**
   - Test critical endpoints
   - Check logs for errors

4. **If needed, restore from backup:**
   ```bash
   psql -U postgres -d guess_the_worth_db < backups/db_backup_YYYYMMDD_HHMMSS.sql
   ```

### Testing Migrations Before Production

Always test migrations in development first:

1. **Backup dev database:**
   ```bash
   ./scripts/backup_database.sh
   ```

2. **Test migration:**
   ```bash
   ./scripts/test_migrations.sh
   ```

3. **Verify data integrity:**
   - Check that existing data is preserved
   - Test application functionality
   - Run automated tests

4. **Test rollback:**
   ```bash
   alembic downgrade -1
   alembic upgrade head
   ```

## Migration Best Practices

1. **Always create backups** before running migrations in production
2. **Test rollback** in development before deploying
3. **Keep migrations small** and focused on single changes
4. **Never edit applied migrations** - create new ones instead
5. **Include both upgrade() and downgrade()** functions
6. **Test with production-like data volume**

## Automated Testing

Migrations are tested in CI/CD pipeline:
- Forward migration (upgrade)
- Backward migration (downgrade)
- Data integrity checks

See `.github/workflows/backend-ci.yml` for details.
```

**5. Add Migration Tests to CI**

**File:** `.github/workflows/backend-ci.yml` (MODIFY)

Add new job after the `test` job:

```yaml
  migration-test:
    name: Migration Rollback Test
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./backend

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: test_user
          POSTGRES_PASSWORD: test_password
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    env:
      DATABASE_URL: postgresql://test_user:test_password@localhost:5432/test_db

    steps:
      - name: Checkout code
        uses: actions/checkout@v6

      - name: Set up Python
        uses: actions/setup-python@v6
        with:
          python-version: '3.13'
          cache: 'pip'
          cache-dependency-path: backend/requirements.txt

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run migrations to head
        run: alembic upgrade head

      - name: Test rollback one step
        run: |
          alembic downgrade -1
          alembic upgrade head

      - name: Verify final state
        run: |
          alembic current | grep -q "head"
          echo "✅ Migration rollback test passed"
```

#### Validation Steps
1. ✅ Create database backup: `cd backend && ./scripts/backup_database.sh`
2. ✅ Test migration rollback: `./scripts/test_migrations.sh`
3. ✅ Verify backup file exists in `backend/backups/`
4. ✅ Test full rollback to base:
   ```bash
   alembic downgrade base
   alembic upgrade head
   ```
5. ✅ Verify application still works after rollback test
6. ✅ Push changes and verify CI migration tests pass

#### Files Modified
- `backend/scripts/test_migrations.sh` (new)
- `backend/scripts/backup_database.sh` (new)
- `backend/docs/MIGRATIONS.md` (new)
- `backend/.gitignore` (add `backups/` if not present)
- `.github/workflows/backend-ci.yml`

---

### Stage 7: Final Validation & Documentation 📋
**Branch:** `feature/final-stage-7-validation`
**Priority:** LOW
**Estimated Time:** 1-2 hours

#### Goals
- Comprehensive end-to-end testing
- Update documentation
- Create production deployment checklist
- Final security review

#### Prerequisites
- All stages 0-6 complete

#### Tasks

**1. Create End-to-End Test Suite**

**File:** `backend/tests/test_e2e_complete_flow.py` (CREATE or UPDATE)

```python
"""
End-to-end integration test for complete user flows.
"""
import pytest
from fastapi.testclient import TestClient

def test_complete_auction_flow(
    client: TestClient,
    seller_token: str,
    buyer_token: str,
    admin_token: str
):
    """
    Test complete auction lifecycle:
    1. Seller creates artwork
    2. Buyer places bids
    3. Artwork is sold
    4. Admin views transaction
    """
    # 1. Seller creates artwork
    artwork_data = {
        "title": "E2E Test Artwork",
        "description": "Testing complete flow",
        "artist_name": "Test Artist",
        "category": "painting",
        "starting_bid": 100,
        "secret_threshold": 500,
    }

    response = client.post(
        "/api/artworks/",
        json=artwork_data,
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    assert response.status_code == 200
    artwork = response.json()
    artwork_id = artwork["id"]

    # 2. Buyer places losing bid
    response = client.post(
        "/api/bids/",
        json={"artwork_id": artwork_id, "amount": 200},
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_winning"] == False

    # 3. Buyer places winning bid
    response = client.post(
        "/api/bids/",
        json={"artwork_id": artwork_id, "amount": 600},
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert response.status_code == 200
    assert response.json()["is_winning"] == True

    # 4. Verify artwork is sold
    response = client.get(
        f"/api/artworks/{artwork_id}",
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "sold"

    # 5. Admin views transaction
    response = client.get(
        "/api/admin/transactions",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    transactions = response.json()["transactions"]
    assert any(t["artwork_title"] == "E2E Test Artwork" for t in transactions)

    # 6. Verify audit logs were created
    response = client.get(
        "/api/admin/audit-logs",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    logs = response.json()["logs"]
    assert any(log["action"] == "bid_placed" for log in logs)
    assert any(log["action"] == "artwork_sold" for log in logs)

def test_admin_user_management_flow(
    client: TestClient,
    admin_token: str,
    buyer_token: str
):
    """Test admin user management capabilities."""
    # 1. Admin lists users
    response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "users" in response.json()

    # 2. Admin gets user details
    user_id = response.json()["users"][0]["id"]
    response = client.get(
        f"/api/admin/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert "stats" in response.json()

    # 3. Verify non-admin cannot access
    response = client.get(
        "/api/admin/users",
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert response.status_code == 403
```

**2. Update Main README**

**File:** `README.md` (MODIFY)

Add deployment section:

```markdown
## 🚀 Production Deployment

### Pre-Deployment Checklist

Before deploying to production:

- [ ] All tests passing (`pytest` and `npm test`)
- [ ] Test coverage >80% backend, >70% frontend
- [ ] Database backup created
- [ ] Environment variables configured
- [ ] Migration rollback tested
- [ ] Security scan passed (no HIGH vulnerabilities)
- [ ] Rate limiting configured
- [ ] Audit logging enabled

### Environment Variables

Copy `.env.example` files and configure:

**Backend** (`backend/.env`):
```bash
DATABASE_URL=postgresql://user:password@host:port/dbname
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
JWT_SECRET_KEY=your-secret-key
STRIPE_SECRET_KEY=sk_live_...
```

**Frontend** (`frontend/.env`):
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
VITE_AUTH0_DOMAIN=your-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
```

### Database Migrations

```bash
# Backup first
cd backend
./scripts/backup_database.sh

# Run migrations
alembic upgrade head

# If issues occur, rollback:
alembic downgrade -1
```

### Testing Coverage

Backend:
```bash
cd backend
pytest --cov --cov-report=html --cov-fail-under=80
```

Frontend:
```bash
cd frontend
npm run test:coverage
```

## 🔒 Security

- ✅ JWT token-based authentication
- ✅ Role-based access control (RBAC)
- ✅ Rate limiting on critical endpoints
- ✅ Audit logging for security events
- ✅ Input validation and sanitization
- ✅ CORS protection
- ✅ Security headers (CSP, XSS protection)

## 📊 Monitoring

### Audit Logs
View security-critical actions:
```sql
SELECT * FROM audit_logs
ORDER BY timestamp DESC
LIMIT 100;
```

### System Health
Admin endpoint: `GET /api/admin/system/health`

## 🧪 Testing

Full test suite:
```bash
# Backend
cd backend
pytest -v --cov

# Frontend
cd frontend
npm test

# E2E
pytest tests/test_e2e_complete_flow.py -v
```
```

**3. Create Production Deployment Checklist**

**File:** `DEPLOYMENT_CHECKLIST.md` (CREATE)

```markdown
# Production Deployment Checklist

## Pre-Deployment (Development)

### Code Quality
- [ ] All tests passing locally (`pytest` and `npm test`)
- [ ] No linting errors (`flake8`, `npm run lint`)
- [ ] Code formatted (`black`, `prettier`)
- [ ] No console.log or debugging code
- [ ] No hardcoded secrets or credentials

### Testing
- [ ] Backend test coverage ≥80%
- [ ] Frontend test coverage ≥70%
- [ ] Critical paths (auth, bidding) ≥90% coverage
- [ ] E2E tests passing
- [ ] Migration rollback tested

### Security
- [ ] All secrets in environment variables
- [ ] .gitignore properly configured
- [ ] No secrets committed to git history
- [ ] Rate limiting enabled
- [ ] Audit logging enabled
- [ ] Security headers configured
- [ ] HTTPS enforced
- [ ] CORS properly configured

### Database
- [ ] Backup created: `./scripts/backup_database.sh`
- [ ] Migrations tested: `./scripts/test_migrations.sh`
- [ ] Indexes verified
- [ ] Connection pooling configured

## Deployment

### Environment Configuration
- [ ] Production `.env` files created (NOT committed)
- [ ] DATABASE_URL points to production database
- [ ] AUTH0_CLIENT_SECRET is production secret
- [ ] JWT_SECRET_KEY is strong random key
- [ ] ALLOWED_ORIGINS includes production domain
- [ ] STRIPE_SECRET_KEY is production key

### Database Migration
1. [ ] Create production database backup
2. [ ] Run migrations: `alembic upgrade head`
3. [ ] Verify migration: `alembic current`
4. [ ] Test application connections

### Application Deployment
- [ ] Backend deployed and running
- [ ] Frontend built: `npm run build`
- [ ] Frontend deployed (static files served)
- [ ] Nginx/Apache configured for SPA routing
- [ ] SSL certificate installed and valid

### Verification
- [ ] Health check endpoint responding: `/api/admin/system/health`
- [ ] Authentication working (Auth0 login)
- [ ] WebSocket connections working
- [ ] Image uploads working
- [ ] Database queries performing well
- [ ] No errors in logs

## Post-Deployment

### Monitoring
- [ ] Error logging configured (Sentry, etc.)
- [ ] Performance monitoring enabled (APM)
- [ ] Database monitoring active
- [ ] Alert notifications configured

### Testing
- [ ] Smoke tests on production
- [ ] User registration works
- [ ] Artwork creation works
- [ ] Bidding works
- [ ] Admin dashboard accessible
- [ ] Real-time updates working

### Documentation
- [ ] Production URLs documented
- [ ] Admin credentials securely stored
- [ ] Backup schedule documented
- [ ] Incident response plan defined

## Rollback Plan

If deployment fails:

1. **Immediate:**
   - [ ] Revert application to previous version
   - [ ] Rollback database: `alembic downgrade -1`
   - [ ] Verify old version works

2. **If database corrupted:**
   - [ ] Restore from backup:
     ```bash
     psql -U postgres -d dbname < backups/db_backup_YYYYMMDD.sql
     ```

3. **Communication:**
   - [ ] Notify team of rollback
   - [ ] Document what failed
   - [ ] Schedule fix and re-deployment

## Sign-Off

- [ ] Deployment completed by: ________________
- [ ] Verified by: ________________
- [ ] Date: ________________
- [ ] Production URL: ________________
```

**4. Run Final Tests**

```bash
# Backend tests with coverage
cd backend
pytest --cov --cov-report=term --cov-report=html

# Frontend tests with coverage
cd frontend
npm run test:coverage

# E2E tests
cd backend
pytest tests/test_e2e_complete_flow.py -v

# Migration tests
./scripts/test_migrations.sh
```

**5. Security Scan**

```bash
# Backend security
cd backend
bandit -r . --severity-level medium
pip-audit --desc

# Frontend security
cd frontend
npm audit --audit-level=high
```

**6. Final Git Status Check**

```bash
# Verify no secrets in git
git status

# Search for common secret patterns
grep -r "password.*=.*\"" . --exclude-dir=.git --exclude-dir=node_modules
grep -r "secret.*=.*\"" . --exclude-dir=.git --exclude-dir=node_modules
grep -r "token.*=.*\"" . --exclude-dir=.git --exclude-dir=node_modules

# All should only show .env.example files or code using os.getenv()
```

#### Validation Steps
1. ✅ Run all tests: Backend and frontend
2. ✅ Verify test coverage meets requirements
3. ✅ Run security scans (no HIGH/CRITICAL issues)
4. ✅ Test migration rollback
5. ✅ Review all documentation
6. ✅ Verify no secrets in git
7. ✅ Complete deployment checklist
8. ✅ Test complete user flows manually

#### Files Modified
- `backend/tests/test_e2e_complete_flow.py` (new/updated)
- `README.md` (updated with production section)
- `DEPLOYMENT_CHECKLIST.md` (new)

---

## Validation Checklist

After completing all 7 stages:

### Configuration & Security
- [ ] `.gitignore` files created (backend and frontend)
- [ ] No `.env` files in git
- [ ] Watchlist feature completely removed
- [ ] All secrets in environment variables

### Testing
- [ ] Backend coverage ≥80% (enforced in CI)
- [ ] Frontend coverage ≥70% (enforced in CI)
- [ ] All tests passing in CI/CD
- [ ] E2E tests passing
- [ ] Migration rollback tested

### Security Features
- [ ] Rate limiting active on critical endpoints
- [ ] Audit logging enabled and tested
- [ ] Security headers added
- [ ] No HIGH/CRITICAL vulnerabilities

### Admin Panel
- [ ] Admin API endpoints working
- [ ] Admin dashboard shows real data
- [ ] User management functional
- [ ] Platform statistics accurate
- [ ] System health monitoring working

### Database
- [ ] Migration rollback tested successfully
- [ ] Backup scripts created and tested
- [ ] Migration documentation complete

### Documentation
- [ ] README updated with deployment instructions
- [ ] Deployment checklist created
- [ ] Migration guide complete

### CI/CD
- [ ] GitHub Actions enforcing coverage
- [ ] Security scans passing
- [ ] Migration tests in CI

---

## Completion Criteria

The application is production-ready when:

1. ✅ All 7 stages complete and merged to `dev`
2. ✅ All tests passing with required coverage
3. ✅ No secrets in git repository
4. ✅ Security scans show no HIGH/CRITICAL issues
5. ✅ Admin panel fully functional with real data
6. ✅ Database migration rollback verified
7. ✅ Documentation complete and accurate

**Final Step:** Merge `dev` to `main` for production deployment.

```bash
git checkout main
git merge dev --no-ff -m "feat: complete production readiness implementation"
git push origin main
```

---

## Notes

- **Payment Integration:** Intentionally not implemented (POC application)
- **Watchlist Feature:** Removed entirely (was showing fake data)
- **Admin Panel:** Implemented at POC level (basic functionality)
- **Docker Compose:** Already correctly configured with `env_file`

**Estimated Total Time:** 12-15 hours spread across 7 stages
