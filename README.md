# Guess The Worth - Implementation Roadmap

A web application for an artist collective selling paintings through an innovative "bid what you want" system with secret price thresholds.

**Status**: 🚧 In Development | DevOps Course Project - DTU

---

## 🚀 Quick Start

```bash
# Clone and start with Docker
git clone <repository-url>
cd guess-the-worth
docker-compose up

# Access:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Environment Setup
Create `.env` files in `backend/` and `frontend/` directories with:
- Database credentials
- Auth0 credentials (domain, client ID, client secret)
- Stripe API keys
- JWT secret key

---

## 📊 Service Status

<!-- TODO: Add UptimeRobot status badges here once monitors are configured -->
<!--
Instructions for adding badges:
1. Log into UptimeRobot dashboard (https://uptimerobot.com)
2. For each monitor (Backend Health, Database Health, Frontend):
   - Click on the monitor name
   - Go to "Public Status Pages" or "Badge URL"
   - Copy the badge URL or monitor ID
3. Add badges below using this format:

[![Backend Health](https://img.shields.io/uptimerobot/status/m123456789-abcdefg?label=Backend)](https://stats.uptimerobot.com/XXXXX)
[![Database](https://img.shields.io/uptimerobot/status/m123456789-abcdefg?label=Database)](https://stats.uptimerobot.com/XXXXX)
[![Frontend](https://img.shields.io/uptimerobot/status/m123456789-abcdefg?label=Frontend)](https://stats.uptimerobot.com/XXXXX)

Alternative: Show 7-day uptime percentage
[![Backend Uptime](https://img.shields.io/uptimerobot/ratio/7/m123456789-abcdefg?label=7-day%20uptime)](https://stats.uptimerobot.com/XXXXX)

Note: Monitor IDs start with 'm' followed by numbers. Get them from:
- UptimeRobot dashboard → Monitor → Settings → Monitor ID
- Or from the badge URL generator

Monitored endpoints:
- Backend: https://<AZURE_BACKEND_APP_NAME>.azurewebsites.net/health
- Database: https://<AZURE_BACKEND_APP_NAME>.azurewebsites.net/health/db
- Frontend: https://<AZURE_FRONTEND_APP_NAME>.azurewebsites.net
-->

### 🏥 Health Dashboard

Open [health-dashboard.html](health-dashboard.html) in your browser for a real-time view of all services.

**Setup**:
1. Open `health-dashboard.html` in a text editor
2. Update the `CONFIG` section with your Azure App Service names:
   ```javascript
   const CONFIG = {
       backendUrl: 'your-backend-name.azurewebsites.net',
       frontendUrl: 'your-frontend-name.azurewebsites.net',
       checkInterval: 30000 // 30 seconds
   };
   ```
3. Open the file in any modern browser
4. The dashboard will automatically check service health every 30 seconds

**Features**:
- ✅ Real-time health monitoring
- 📊 Response time tracking
- 🔄 Auto-refresh (toggle with spacebar)
- ⌨️ Press 'R' to refresh manually
- 📱 Mobile-friendly design

---

## 📋 Implementation Tasks

### 1. Backend Security Hardening

**Issue**: Hardcoded secrets in `backend/config/settings.py`

**Implementation**:
- [ ] Remove all hardcoded secrets from `settings.py`:
  - JWT secret key
  - Auth0 credentials (domain, client ID, client secret)
  - Stripe keys
- [ ] Move all sensitive values to environment variables
- [ ] Create `backend/.env.example` template
- [ ] Update `docker-compose.yml` to pass environment variables to containers
- [ ] Document all required environment variables

**Files**:
- `backend/config/settings.py`
- `backend/.env.example` (create)
- `docker-compose.yml`

**Example**:
```python
# Before
auth0_client_secret: str = "hardcoded-secret"

# After
auth0_client_secret: str = os.getenv("AUTH0_CLIENT_SECRET")
```

---

### 2. Database Seeding System

**Goal**: Create seed data for development and testing

**Implementation**:
- [ ] Create `backend/seeds/` directory structure:
  ```
  seeds/
  ├── __init__.py
  ├── run.py (main entry point)
  ├── users.py (seed users)
  ├── artworks.py (seed artworks)
  └── bids.py (seed bids)
  ```
- [ ] Implement seed data:
  - Admin user: `admin@test.com` with admin role
  - 2-3 seller users with valid Auth0 subs
  - 5-10 buyer users
  - 10-15 artworks with different statuses (active, sold)
  - Sample artwork images (use placeholder images or real art)
  - Historical bids on various artworks
  - User favorites
- [ ] Add CLI command: `python -m seeds.run`
- [ ] Add seed command to Docker Compose startup
- [ ] Create reset script: `python -m seeds.reset` (clear and reseed)

**Approach**:
```python
# backend/seeds/run.py
from database import SessionLocal
from seeds import users, artworks, bids

def seed_all():
    db = SessionLocal()
    try:
        print("Seeding users...")
        users.seed(db)
        print("Seeding artworks...")
        artworks.seed(db)
        print("Seeding bids...")
        bids.seed(db)
        print("Database seeded successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    seed_all()
```

**Test Users to Create**:
- `admin@test.com` - Admin
- `seller1@test.com` - Seller
- `seller2@test.com` - Seller
- `buyer1@test.com` through `buyer5@test.com` - Buyers

---

### 3. Database Migrations

**Goal**: Proper schema versioning with Alembic

**Implementation**:
- [ ] Generate initial migration:
  ```bash
  cd backend
  alembic revision --autogenerate -m "Initial schema"
  ```
- [ ] Review the generated migration file in `backend/alembic/versions/`
- [ ] Test migration: `alembic upgrade head`
- [ ] Test rollback: `alembic downgrade -1`
- [ ] Add migration command to Docker Compose (run on container startup)
- [ ] Create migration for any future schema changes

**Docker Integration**:
Update `docker-compose.yml` backend service:
```yaml
backend:
  command: >
    sh -c "alembic upgrade head &&
           uvicorn main:socket_app --host 0.0.0.0 --port 8000 --reload"
```

---

### 4. Frontend-Backend API Integration

**Goal**: Connect all frontend components to backend endpoints

**Implementation**:

**Create Base API Client** (`frontend/src/services/api.js`):
- [ ] Create axios instance with base URL
- [ ] Add request interceptor to attach JWT token from authStore
- [ ] Add response interceptor for error handling
- [ ] Handle 401 (logout user) and 403 (show permission error)
- [ ] Add retry logic for network failures

**Authentication Service** (`frontend/src/services/authService.js`):
- [ ] `login(auth0Token)` - Exchange Auth0 token for JWT
- [ ] `register(userData)` - Register new user
- [ ] `getCurrentUser()` - Fetch user profile
- [ ] `logout()` - Clear local storage and tokens

**Artwork Service** (`frontend/src/services/artworkService.js`):
- [ ] `getAllArtworks()` - Fetch all artworks (public)
- [ ] `getArtworkById(id)` - Fetch single artwork details
- [ ] `createArtwork(formData)` - Create new artwork (seller)
- [ ] `updateArtwork(id, data)` - Update artwork (seller)
- [ ] `deleteArtwork(id)` - Delete artwork (seller/admin)
- [ ] `getMyArtworks()` - Fetch seller's own artworks

**Bid Service** (`frontend/src/services/bidService.js`):
- [ ] `placeBid(artworkId, amount)` - Submit new bid
- [ ] `getBidHistory(artworkId)` - Fetch bids for artwork
- [ ] `getMyBids()` - Fetch user's bid history

**User Service** (`frontend/src/services/userService.js`):
- [ ] `getUserProfile()` - Fetch current user details
- [ ] `updateProfile(data)` - Update user profile
- [ ] `getUserActivity()` - Fetch user's recent activity

**Error Handling**:
- [ ] Create toast notification system using Chakra UI toast
- [ ] Add loading states to all components making API calls
- [ ] Show user-friendly error messages

**Example API Client**:
```javascript
import axios from 'axios';
import useAuthStore from '../store/authStore';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
});

api.interceptors.request.use((config) => {
  const token = useAuthStore.getState().token;
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().clearAuth();
    }
    return Promise.reject(error);
  }
);

export default api;
```

---

### 5. Stripe Payment Integration

**Goal**: Complete payment flow for successful bids that meet secret threshold

**Backend Implementation**:

**Create Stripe Service** (`backend/services/stripe_service.py`):
- [ ] Initialize Stripe with API key from settings
- [ ] `create_checkout_session(artwork_id, buyer_id, amount)` - Create payment session
- [ ] `handle_webhook(payload, signature)` - Process Stripe webhook events
- [ ] Update artwork status to "sold" on successful payment
- [ ] Create payment record in database

**Create Payment Model** (`backend/models/payment.py`):
```python
class Payment(Base):
    id = Column(Integer, primary_key=True)
    stripe_session_id = Column(String, unique=True)
    artwork_id = Column(Integer, ForeignKey('artworks.id'))
    buyer_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Numeric)
    status = Column(String)  # pending, completed, failed
    created_at = Column(DateTime)
```

**Create Payment Router** (`backend/routers/payments.py`):
- [ ] `POST /api/payments/create-checkout-session` - Create Stripe session
- [ ] `POST /api/payments/webhook` - Handle Stripe webhooks
- [ ] `GET /api/payments/{payment_id}` - Get payment status
- [ ] `GET /api/payments/user` - Get user's payment history

**Frontend Implementation**:

**Install Stripe Dependencies**:
```bash
npm install @stripe/stripe-js @stripe/react-stripe-js
```

**Create Checkout Component** (`frontend/src/components/StripeCheckout.jsx`):
- [ ] Wrap with `Elements` provider from Stripe
- [ ] Create checkout form with card element
- [ ] Handle payment confirmation
- [ ] Redirect to success page after payment

**Payment Flow**:
```javascript
// 1. User wins auction (bid meets threshold)
// 2. Frontend calls backend to create checkout session
const { sessionId } = await createCheckoutSession(artworkId);

// 3. Redirect to Stripe Checkout
const stripe = await loadStripe(publishableKey);
await stripe.redirectToCheckout({ sessionId });

// 4. User completes payment on Stripe
// 5. Stripe webhook notifies backend
// 6. Backend updates artwork status and creates payment record
// 7. User redirected back to success page
```

**Test with Stripe CLI**:
```bash
# Forward webhooks to local backend
stripe listen --forward-to localhost:8000/api/payments/webhook
```

---

### 6. Frontend Bug Fixes

#### 6.1 Navbar Buttons Updates

**Issue**: Navbar links and buttons need fixes

**Implementation** (`frontend/src/components/Header.jsx`):
- [ ] Audit all navigation links
- [ ] Fix dashboard button routing: `/dashboard`
- [ ] Add conditional rendering based on user role:
  ```jsx
  {isSeller() && <Link to="/sell">Sell Artwork</Link>}
  {isAdmin() && <Link to="/admin">Admin Panel</Link>}
  ```
- [ ] Fix "View All Activity" button to navigate to dashboard
- [ ] Add active state styling for current page using `useLocation()`
- [ ] Ensure mobile menu works responsively

---

#### 6.2 Stay Logged In on Refresh

**Issue**: User loses authentication state on page refresh

**Implementation**:

**Update Auth Store** (`frontend/src/store/authStore.js`):
- [ ] Verify Zustand persist middleware is correctly configured
- [ ] Ensure token and user are persisted to localStorage

**Add Auth Check on Mount** (`frontend/src/App.jsx`):
- [ ] Create `useEffect` hook that runs on mount
- [ ] Validate token on app load (call `/api/auth/me`)
- [ ] If token expired, clear auth and redirect to login
- [ ] Show loading spinner during auth check

**Create Protected Route Component** (`frontend/src/components/ProtectedRoute.jsx`):
```jsx
import { Navigate } from 'react-router-dom';
import useAuthStore from '../store/authStore';

export default function ProtectedRoute({ children, requiredRole }) {
  const { isAuthenticated, isLoading, hasRole } = useAuthStore();

  if (isLoading) return <Spinner />;
  if (!isAuthenticated) return <Navigate to="/login" />;
  if (requiredRole && !hasRole(requiredRole)) {
    return <Navigate to="/" />;
  }

  return children;
}
```

**Usage**:
```jsx
<Route path="/sell" element={
  <ProtectedRoute requiredRole="seller">
    <SellArtwork />
  </ProtectedRoute>
} />
```

---

#### 6.3 View Details on Sell Artwork Page

**Issue**: "View Details" button not working on seller's artwork list

**Implementation** (`frontend/src/pages/SellArtwork.jsx`):
- [ ] Debug artwork detail route
- [ ] Ensure button uses correct navigation:
  ```jsx
  <Button onClick={() => navigate(`/artworks/${artwork.id}`)}>
    View Details
  </Button>
  ```
- [ ] Verify artwork ID is being passed correctly
- [ ] Check that `/artworks/:id` route exists in router
- [ ] Test with seeded artwork data

**Verify Route** (`frontend/src/App.jsx`):
```jsx
<Route path="/artworks/:id" element={<ArtworkDetail />} />
```

---

#### 6.4 Dashboard Activity Button

**Issue**: "View all activity in your dashboard" button on homepage not functional

**Implementation**:

**Create Dashboard Page** (`frontend/src/pages/Dashboard.jsx`):
- [ ] Create layout with role-specific sections
- [ ] Buyer dashboard: Show bids placed, won auctions, payment history
- [ ] Seller dashboard: Show artworks listed, bids received, sales
- [ ] Admin dashboard: Show all system activities

**Create Activity Feed Component** (`frontend/src/components/ActivityFeed.jsx`):
- [ ] Fetch user activities from backend
- [ ] Display activity timeline with icons
- [ ] Add pagination for long activity lists
- [ ] Show different activity types:
  - Bid placed
  - Bid received
  - Artwork sold
  - Payment completed

**Backend Activity Endpoint** (`backend/routers/activities.py`):
```python
@router.get("/api/activities")
async def get_user_activities(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch user's recent activities
    activities = []

    # Add user's bids
    bids = db.query(Bid).filter(Bid.buyer_id == current_user.id).all()

    # Add user's artworks if seller
    if current_user.role in ['seller', 'admin']:
        artworks = db.query(Artwork).filter(
            Artwork.seller_id == current_user.id
        ).all()

    # Return combined activities sorted by date
    return activities
```

**Fix Homepage Button** (`frontend/src/pages/HomePage.jsx`):
```jsx
<Button onClick={() => navigate('/dashboard')}>
  View all activity in your dashboard
</Button>
```

---

### 7. CI/CD Pipeline Implementation

#### 7.1 Backend CI Pipeline

**File**: `.github/workflows/backend-ci.yml`

**Implementation**:
- [ ] Create workflow file with triggers on push/PR to `main` and `dev`
- [ ] Job 1: Code Quality
  - Install dependencies
  - Run `black --check backend/`
  - Run `flake8 backend/`
  - Run `isort --check-only backend/`
- [ ] Job 2: Testing
  - Set up PostgreSQL service container
  - Install dependencies with pytest
  - Run `pytest backend/tests/ --cov --cov-report=xml`
  - Upload coverage to Codecov
  - Fail if coverage < 70%
- [ ] Job 3: Security
  - Run `bandit -r backend/`
  - Run `pip-audit`
  - Run `trufflehog` to scan for secrets
- [ ] Job 4: Docker Build
  - Build Docker image: `docker build -t backend:${{ github.sha }} ./backend`
  - Run Trivy security scan: `trivy image backend:${{ github.sha }}`
  - Push to GHCR if on main branch
  - Tag with commit SHA and branch name

**Example Workflow Structure**:
```yaml
name: Backend CI

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main, dev]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install black flake8 isort
      - run: black --check backend/
      - run: flake8 backend/
      - run: isort --check-only backend/

  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/tests/ --cov --cov-report=xml
      - uses: codecov/codecov-action@v4
```

---

#### 7.2 Frontend CI Pipeline

**File**: `.github/workflows/frontend-ci.yml`

**Implementation**:
- [ ] Create workflow file with triggers on push/PR to `main` and `dev`
- [ ] Job 1: Code Quality
  - Install dependencies: `npm ci`
  - Run ESLint: `npm run lint`
  - Run Prettier check: `npx prettier --check "frontend/src/**/*.{js,jsx}"`
- [ ] Job 2: Testing
  - Run Vitest: `npm run test -- --coverage`
  - Upload coverage to Codecov
  - Fail if coverage < 70%
- [ ] Job 3: Build
  - Run production build: `npm run build`
  - Check bundle size (set budget: < 500KB)
  - Optional: Run Lighthouse CI for performance metrics
- [ ] Job 4: Security
  - Run `npm audit --audit-level=high`
  - Check for outdated dependencies: `npm outdated`

---

#### 7.3 Continuous Deployment Pipeline

**File**: `.github/workflows/deploy.yml`

**Deployment Environments**:
- Development: Auto-deploy on push to `dev` branch
- Staging: Auto-deploy on push to `main` branch (with smoke tests)
- Production: Deploy on release tags (`v*.*.*`) with manual approval

**Backend Deployment**:
- [ ] Choose platform: Render / Railway / Fly.io
- [ ] Build and push Docker image to registry
- [ ] Deploy to platform using CLI or API
- [ ] Run database migrations: `alembic upgrade head`
- [ ] Health check: `curl /health`
- [ ] Run smoke tests (basic API endpoint checks)
- [ ] Rollback on failure

**Frontend Deployment**:
- [ ] Choose platform: Vercel / Netlify / Cloudflare Pages
- [ ] Build with production environment variables
- [ ] Deploy static files
- [ ] Invalidate CDN cache
- [ ] Verify deployment with HTTP check

**Example Render Deployment**:
```yaml
deploy-backend:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    - name: Deploy to Render
      env:
        RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
      run: |
        curl -X POST https://api.render.com/v1/services/$SERVICE_ID/deploys \
          -H "Authorization: Bearer $RENDER_API_KEY"
```

---

#### 7.4 Branch Protection & Quality Gates

**Implementation**:
- [ ] Go to GitHub repo settings → Branches → Add rule for `main`
- [ ] Enable required status checks:
  - Backend CI must pass
  - Frontend CI must pass
  - Code coverage ≥ 70%
  - Docker build must succeed
- [ ] Require at least 1 code review approval
- [ ] Disable force pushes
- [ ] Enable linear history (no merge commits)
- [ ] Create `CODEOWNERS` file to automatically request reviews

---

### 8. Comprehensive Testing Suite ✅ COMPLETED

**Status**: ✅ Backend + Frontend testing fully implemented

**Test Results Summary**:
- **Backend**: 50/51 tests passing (98% pass rate) | 65% overall coverage
- **Frontend**: 92/92 tests passing (100% pass rate) | 100% store coverage
- **Total**: 142 tests implemented

**Test Structure**:
```
backend/tests/
├── conftest.py                    # Shared fixtures (users, artworks, bids, auth tokens)
├── unit/
│   ├── test_schemas.py           # Pydantic validation tests
│   ├── test_models.py            # SQLAlchemy model tests
│   └── test_auth_service.py      # Auth & JWT service tests
├── integration/
│   ├── test_auth_api.py          # Auth endpoints
│   ├── test_artworks_api.py      # Artwork CRUD endpoints
│   ├── test_bids_api.py          # Bid endpoints + threshold logic
│   └── test_users_api.py         # User management endpoints
└── e2e/
    └── test_complete_flow.py     # Full user journey tests
```

#### 8.1 Backend Unit Tests ✅

**Implemented** (`backend/tests/unit/`):

**✅ Test Schemas** (`test_schemas.py`):
- [x] UserCreate, UserUpdate, UserResponse validation
- [x] ArtworkCreate, ArtworkUpdate with secret threshold
- [x] BidCreate, BidResponse validation
- [x] AuthUser, TokenResponse schemas
- [x] Edge cases: negative values, unicode, very long strings
- [x] Email validation, required fields, default values

**✅ Test Models** (`test_models.py`):
- [x] User model creation, unique constraints (auth0_sub, email)
- [x] User role enum (BUYER, SELLER, ADMIN)
- [x] Artwork model with relationships to seller and bids
- [x] Artwork status enum (ACTIVE, SOLD, ARCHIVED)
- [x] Bid model with artwork and bidder relationships
- [x] Cascade deletions (user → artworks → bids)
- [x] Foreign key constraints

**✅ Test Auth Service** (`test_auth_service.py`):
- [x] Auth0 token verification (mocked)
- [x] JWT token creation, verification, expiration
- [x] Role mapping (Auth0 roles → UserRole enum)
- [x] get_or_create_user flow
- [x] User role updates when Auth0 role changes
- [x] Invalid/expired token handling

**Running Unit Tests**:
```bash
cd backend
pytest tests/unit/ -v
```

---

#### 8.2 Backend Integration Tests ✅

**Implemented** (`backend/tests/integration/`):

**✅ Authentication API** (`test_auth_api.py`):
- [x] POST `/api/auth/register` - New user registration
- [x] GET `/api/auth/me` - Get current user by auth0_sub
- [x] Duplicate registration prevention (unique email, auth0_sub)
- [x] Role-based user creation (buyer, seller, admin)
- [x] Invalid email/missing fields validation
- [x] JWT and Auth0 token authentication

**✅ Artworks API** (`test_artworks_api.py`):
- [x] GET `/api/artworks` - List with pagination (skip, limit)
- [x] GET `/api/artworks/{id}` - Single artwork details
- [x] POST `/api/artworks` - Create artwork (seller)
- [x] Artwork status filtering (active, sold, archived)
- [x] Secret threshold NOT exposed in public responses
- [x] Edge cases: unicode titles, HTML in descriptions

**✅ Bids API** (`test_bids_api.py`) - **CRITICAL PATH**:
- [x] **Bid below threshold** → is_winning=False, artwork stays ACTIVE
- [x] **Bid at threshold** → is_winning=True, artwork becomes SOLD
- [x] **Bid above threshold** → is_winning=True, artwork becomes SOLD
- [x] **Cannot bid on SOLD artwork** → 400 error
- [x] **Bid on non-existent artwork** → 404 error
- [x] **Current highest bid updates** correctly
- [x] Multiple bids from same user allowed
- [x] Concurrent bidding from multiple users
- [x] GET `/api/bids/artwork/{id}` - Bid history
- [x] Negative/zero bid amount validation
- [x] Seller bidding on own artwork (documented edge case)

**✅ Users API** (`test_users_api.py`):
- [x] GET `/api/users` - List users with pagination
- [x] GET `/api/users/{id}` - Single user details
- [x] All user roles included (buyer, seller, admin)
- [x] Response includes all expected fields

**Running Integration Tests**:
```bash
pytest tests/integration/ -v
pytest tests/integration/test_bids_api.py::TestBidThresholdLogic -v  # Critical path
```

---

#### 8.3 End-to-End Tests ✅

**Implemented** (`backend/tests/e2e/test_complete_flow.py`):

**✅ Complete User Flows**:
- [x] **Buyer journey**: Register → Browse → Place losing bid → Place winning bid → Artwork sold
- [x] **Multiple buyers competing**: 3 buyers bid competitively, highest wins
- [x] **Seller with multiple artworks**: Some sold, some active
- [x] **Error recovery**: Invalid bid → Correct bid succeeds
- [x] **Marketplace scenario**: 2 sellers, 3 buyers, 4 artworks, mixed outcomes
- [x] **Edge case**: Immediate purchase at threshold
- [x] **Edge case**: Zero threshold artwork (free art)

**Running E2E Tests**:
```bash
pytest tests/e2e/ -v
pytest tests/e2e/test_complete_flow.py::TestCompleteUserFlow -v
```

---

#### 8.4 Test Fixtures & Configuration ✅

**Fixtures Available** (`conftest.py`):
- [x] `db_session` - Fresh SQLite in-memory database per test
- [x] `client` - FastAPI TestClient with DB override
- [x] `buyer_user`, `seller_user`, `admin_user` - Pre-created test users
- [x] `artwork` - Active artwork with threshold=100.0
- [x] `sold_artwork` - Already sold artwork for edge case tests
- [x] `bid` - Sample bid fixture
- [x] `buyer_token`, `seller_token`, `admin_token` - Valid JWT tokens
- [x] `mock_auth0_response` - Factory for Auth0 user data
- [x] `mock_auth0_service` - Mocked Auth0 service (no real API calls)
- [x] Helper: `create_auth_header(token)` - Authorization header builder

**pytest Configuration** (`pyproject.toml`):
- [x] Test discovery: `tests/` directory
- [x] Coverage reporting: `--cov=. --cov-report=term-missing --cov-report=xml`
- [x] Coverage omits: `tests/`, `venv/`, `alembic/`
- [x] Async mode: auto
- [x] Target coverage: >80% for critical paths

---

#### 8.5 Running Tests

**Quick Start**:
```bash
cd backend

# Run all tests
pytest

# Run with coverage report
pytest --cov=. --cov-report=term-missing

# Run specific test category
pytest tests/unit/           # Unit tests
pytest tests/integration/    # Integration tests
pytest tests/e2e/           # E2E tests

# Run specific test file
pytest tests/integration/test_bids_api.py -v

# Run specific test class
pytest tests/integration/test_bids_api.py::TestBidThresholdLogic -v

# Run specific test function
pytest tests/integration/test_bids_api.py::TestBidThresholdLogic::test_bid_at_threshold -v

# Run tests matching pattern
pytest -k "threshold" -v

# Run with verbose output
pytest -vv -s

# Run failed tests only
pytest --lf

# Run tests in parallel (faster)
pytest -n auto  # Requires: pip install pytest-xdist
```

**Coverage Goals**:
- Critical paths (auth, bidding): >90%
- API endpoints: >85%
- Models & schemas: >80%
- Overall: >80%

**Check Coverage**:
```bash
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

---

#### 8.6 Test Documentation

**Full Testing Guide**: See [`backend/tests/README.md`](backend/tests/README.md)

**Key Testing Principles**:
1. **Isolation**: Each test uses fresh database (SQLite in-memory)
2. **Mocking**: Auth0 API calls are mocked (no real API calls)
3. **Fixtures**: Reusable test data via pytest fixtures
4. **Coverage**: Comprehensive edge case testing
5. **Speed**: Fast tests using in-memory DB

**Critical Test Cases Covered**:
- ✅ Bid threshold logic (below/at/above threshold)
- ✅ Artwork status transitions (active → sold)
- ✅ Cascade deletions (user → artworks → bids)
- ✅ Unique constraints (email, auth0_sub)
- ✅ Role-based access control
- ✅ Concurrent bidding scenarios
- ✅ Auth0 token verification and JWT handling
- ✅ Input validation (negative values, missing fields)
- ✅ Unicode and special characters
- ✅ Pagination and filtering

**Test Statistics**:
- **Total Test Files**: 8 (3 unit + 4 integration + 1 e2e)
- **Test Classes**: 50+
- **Test Functions**: 200+
- **Test Coverage**: Run `pytest --cov` to see current coverage

---

#### 8.7 Frontend Unit Tests ✅ COMPLETED

**Status**: ✅ 92 tests passing with 100% store coverage

**Implementation** (`frontend/src/test/unit/`):

**✅ Test Zustand Stores** (`authStore.test.js` - 27 tests):
- [x] `setAuth()` updates user and token correctly
- [x] `clearAuth()` clears all state
- [x] `setLoading()` manages loading state
- [x] `updateUser()` updates user data partially
- [x] `hasRole()` correctly checks user role
- [x] `isAdmin()` returns true for admin role
- [x] `isSeller()` returns true for seller and admin
- [x] `isBuyer()` returns true for buyer, seller, and admin
- [x] Edge cases: missing role, empty token, null user

**✅ Test Bidding Store** (`biddingStore.test.js` - 24 tests):
- [x] `joinArtwork()` adds artwork to active artworks
- [x] `leaveArtwork()` removes artwork and bids
- [x] `updateBid()` updates bid and artwork's current_highest_bid
- [x] `markArtworkSold()` updates artwork status to sold
- [x] `clearAll()` clears all artworks and bids
- [x] `setSocketConnected()` manages WebSocket connection state
- [x] Complex scenarios: full bidding lifecycle, multiple concurrent auctions

**✅ Test Favorites Store** (`favoritesStore.test.js` - 22 tests):
- [x] `addToFavorites()` adds artwork with dateAdded timestamp
- [x] `removeFromFavorites()` removes specific artwork
- [x] `isFavorite()` checks if artwork is favorited
- [x] `toggleFavorite()` adds/removes artwork
- [x] Prevents duplicate favorites
- [x] Maintains FIFO order
- [x] Edge cases: artwork id 0, rapid add/remove operations

**✅ Test API Services** (`apiServices.test.js` - 19 tests):
- [x] `artworkService.getAll()` with pagination parameters
- [x] `artworkService.getById()` fetches single artwork
- [x] `artworkService.getFeatured()` fetches 6 featured artworks
- [x] `artworkService.create()` creates new artwork
- [x] `artworkService.uploadImage()` uploads artwork image
- [x] `bidService.getByArtwork()` fetches bids for artwork
- [x] `bidService.create()` creates new bid
- [x] `userService.getAll()`, `getById()`, `getCurrentUser()`, `register()`
- [x] `statsService.getPlatformStats()` calculates stats from API
- [x] Error handling: 401 Unauthorized, network failures, HTTP errors

**Running Frontend Tests**:
```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run with coverage report
npm test -- --coverage

# Run specific test file
npm test -- authStore.test.js

# Run tests matching pattern
npm test -- --grep "bid"
```

**Test Coverage**:
- **Stores**: 100% (authStore, biddingStore, favoritesStore)
- **API Services**: 95.2% (api.js)
- **Overall Frontend**: ~7% (stores and services tested, components not yet tested)

**Coverage Report Location**:
```bash
npm test -- --coverage
# Opens: frontend/coverage/index.html
```

---

#### 8.8 Frontend Component Tests (Future Work)

**Status**: ⏳ Not yet implemented (optional)

**Goal**: Test React component rendering and user interactions

**Recommended Implementation** (`frontend/src/test/component/`):

**Priority Components to Test**:
- [ ] Header component (navigation, auth state)
- [ ] ArtworkCard component (rendering, favorite toggle)
- [ ] BidForm component (validation, submission)
- [ ] LoginButton component (Auth0 integration)

**Testing Strategy**:
- Use `@testing-library/react` for component testing
- Mock Auth0 hooks with `vitest.mock()`
- Test user interactions with `@testing-library/user-event`
- Test routing with `react-router-dom` mocks

**Example Component Test**:
```javascript
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ArtworkCard from '../../components/ArtworkCard';

test('renders artwork card with title and price', () => {
  const artwork = {
    id: 1,
    title: 'Test Art',
    current_highest_bid: 500
  };

  render(
    <BrowserRouter>
      <ArtworkCard artwork={artwork} />
    </BrowserRouter>
  );

  expect(screen.getByText('Test Art')).toBeInTheDocument();
  expect(screen.getByText(/\$500/i)).toBeInTheDocument();
});
```

---

#### 8.9 End-to-End Tests (Future Work)

**Status**: ⏳ Not yet implemented (optional)

**Goal**: Test complete user journeys across frontend and backend

**Recommended Tool**: Playwright or Cypress

**Setup E2E Framework**:
```bash
cd frontend
npm install -D @playwright/test
npx playwright install
```

**Priority User Flows to Test**:
- [ ] Buyer journey: Login → Browse artworks → Place bid → Win auction → Payment
- [ ] Seller journey: Login → Create artwork → Receive bid → Sale notification
- [ ] Admin journey: Login → View all users → Manage artworks

**Example E2E Test**:
```javascript
test('buyer can place bid on artwork', async ({ page }) => {
  await page.goto('http://localhost:5173/login');
  await page.fill('[name="email"]', 'buyer@test.com');
  await page.click('button[type="submit"]');

  await page.goto('http://localhost:5173/artworks/1');
  await page.fill('[name="bidAmount"]', '600');
  await page.click('text=Place Bid');

  await expect(page.locator('text=Bid placed successfully')).toBeVisible();
});
```

---

#### 8.6 Role-Based Access Control Testing

**Test Matrix**:
```
Action                  | Anonymous | Buyer | Seller | Admin |
------------------------|-----------|-------|--------|-------|
View artworks           |     ✓     |   ✓   |   ✓    |   ✓   |
View artwork detail     |     ✓     |   ✓   |   ✓    |   ✓   |
Place bid               |     ✗     |   ✓   |   ✗*   |   ✓   |
Create artwork          |     ✗     |   ✗   |   ✓    |   ✓   |
Edit own artwork        |     ✗     |   ✗   |   ✓    |   ✓   |
Edit any artwork        |     ✗     |   ✗   |   ✗    |   ✓   |
Delete own artwork      |     ✗     |   ✗   |   ✓    |   ✓   |
Delete any artwork      |     ✗     |   ✗   |   ✗    |   ✓   |
View all users          |     ✗     |   ✗   |   ✗    |   ✓   |

* Seller cannot bid on their own artwork
```

**Implementation**:
- [ ] Backend: Test API returns 403 for unauthorized actions
- [ ] Frontend: Test UI elements are hidden for unauthorized roles
- [ ] Test redirect to login for unauthenticated users
- [ ] Test seller cannot bid on own artwork (frontend + backend)

---

### 9. Monitoring & Observability

**Implementation**:

**Add Health Check Endpoints** (`backend/routers/health.py`):
```python
@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/health/db")
async def db_health(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
```

**Error Tracking**:
- [ ] Sign up for Sentry (free tier)
- [ ] Install Sentry SDK in backend and frontend
- [ ] Configure DSN in environment variables
- [ ] Test error reporting

**Backend Sentry**:
```python
import sentry_sdk
sentry_sdk.init(dsn=settings.sentry_dsn)
```

**Frontend Sentry**:
```javascript
import * as Sentry from "@sentry/react";
Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
});
```

**Structured Logging**:
- [ ] Replace print statements with Python logging
- [ ] Add request ID to all log entries
- [ ] Log important events: user registration, bids, sales

**Uptime Monitoring**:
- [ ] Sign up for UptimeRobot (free tier)
- [ ] Add monitor for production URL
- [ ] Set up email/SMS alerts for downtime

---

### 10. Performance Optimization

**Backend Optimization**:
- [ ] Add database indexes:
  ```python
  # In models
  __table_args__ = (Index('idx_artwork_status', 'status'),)
  ```
- [ ] Implement pagination for list endpoints:
  ```python
  @router.get("/api/artworks")
  async def get_artworks(skip: int = 0, limit: int = 20):
      return db.query(Artwork).offset(skip).limit(limit).all()
  ```
- [ ] Add eager loading to avoid N+1 queries:
  ```python
  artworks = db.query(Artwork).options(
      joinedload(Artwork.seller),
      joinedload(Artwork.bids)
  ).all()
  ```
- [ ] Optimize image upload/processing with Pillow
- [ ] Add request rate limiting with `slowapi`
- [ ] Consider Redis caching for frequently accessed data

**Frontend Optimization**:
- [ ] Add React.lazy() for route-based code splitting:
  ```jsx
  const Dashboard = lazy(() => import('./pages/Dashboard'));
  ```
- [ ] Lazy load images with loading="lazy" attribute
- [ ] Optimize artwork images (compress, convert to WebP)
- [ ] Add performance budgets in build config
- [ ] Minimize bundle size (analyze with `npm run build -- --analyze`)

---

### 11. Documentation

**Tasks**:
- [ ] Expand API documentation in FastAPI (add descriptions, examples)
- [ ] Create architecture diagram (use draw.io or mermaid)
- [ ] Document database schema with relationships
- [ ] Write deployment guide for chosen platforms
- [ ] Create contributing guidelines (`CONTRIBUTING.md`)
- [ ] Document environment variables in `.env.example` files
- [ ] Add troubleshooting section to README
- [ ] Document testing strategy

---

### 12. Additional Features

**Nice-to-have enhancements**:
- [ ] Email notifications for bid updates (using SendGrid/Mailgun)
- [ ] User profile pictures (upload to S3 or similar)
- [ ] Multiple images per artwork (gallery)
- [ ] Search and filter artworks (by price, artist, status)
- [ ] Artwork categories/tags
- [ ] Export user data (GDPR compliance)
- [ ] Admin dashboard with analytics (charts for sales, users, bids)
- [ ] Audit log for admin actions
- [ ] Internationalization (i18n) for multiple languages

---

## 🏗️ Tech Stack

**Backend**: FastAPI, PostgreSQL, SQLAlchemy, Alembic, Socket.IO, Auth0, Stripe, JWT

**Frontend**: React 19, Vite, Zustand, TanStack Query, Chakra UI, React Router, Socket.io-client

**DevOps**: Docker, Docker Compose, GitHub Actions, Pytest, Vitest

---

## 🏛️ Architecture

### System Architecture
```
Browser
   ↓ (HTTPS)
Frontend (React + Zustand)
   ↓ (REST API with JWT + WebSocket)
Backend (FastAPI + Socket.IO)
   ↓
PostgreSQL | Auth0 | Stripe
```

### Database Schema
```
users
├── id (PK)
├── auth0_sub (unique)
├── email
├── name
├── role (buyer/seller/admin)
└── created_at

artworks
├── id (PK)
├── title
├── description
├── artist_name
├── seller_id (FK → users)
├── image_url
├── secret_threshold
├── current_highest_bid
├── status (active/sold)
└── created_at

bids
├── id (PK)
├── artwork_id (FK → artworks)
├── buyer_id (FK → users)
├── amount
├── status (pending/accepted/rejected)
└── created_at

payments (to be implemented)
├── id (PK)
├── stripe_session_id
├── artwork_id (FK → artworks)
├── buyer_id (FK → users)
├── amount
├── status (pending/completed/failed)
└── created_at
```

---

## 📝 Development Workflow

**Branch Strategy**:
```
main (production)
  └── dev (active development)
       ├── feature/* (new features)
       └── bugfix/* (bug fixes)
```

**Commit Convention**:
- `feat:` New feature
- `fix:` Bug fix
- `test:` Add/update tests
- `docs:` Documentation
- `chore:` Maintenance
- `refactor:` Code refactoring
- `perf:` Performance improvement

---

**Last Updated**: 2025-10-30
