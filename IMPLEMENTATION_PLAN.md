# Implementation Plan: Database Integration & API Completion
### Guess The Worth - Moving from Hardcoded Data to Database-Driven Application

**Document Version:** 1.0
**Created:** 2025-01-22
**Status:** Ready for Implementation

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Analysis Summary](#analysis-summary)
3. [Pre-Implementation Checklist](#pre-implementation-checklist)
4. [Git Workflow & Branching Strategy](#git-workflow--branching-strategy)
5. [Implementation Stages](#implementation-stages)
6. [Post-Implementation Verification](#post-implementation-verification)

---

## Overview

### Current State
The Guess The Worth application is currently a **functional prototype** with:
- ✅ Backend API endpoints (basic CRUD)
- ✅ Database models and schemas
- ✅ Frontend UI components
- ❌ **Most frontend pages use hardcoded mock data**
- ❌ **Critical security vulnerabilities in authentication/authorization**
- ❌ **No real-time bidding functionality**
- ❌ **Missing database indexes and optimizations**

### Goals
Transform the application into a **production-ready, database-driven platform** by:
1. **Securing** authentication and authorization
2. **Integrating** frontend with backend APIs
3. **Implementing** real-time bidding features
4. **Optimizing** database performance
5. **Validating** all functionality with comprehensive tests

### Approach
- **Security-first but balanced**: Critical security fixes early, then feature work
- **Medium-large stages**: Each stage is substantial but fits within Claude Code context window
- **GitFlow branching**: Feature branches for each stage, merge to `dev`, then `main`
- **Validation per stage**: Basic testing during implementation, comprehensive suite at end

---

## Analysis Summary

This implementation plan addresses findings from two comprehensive analyses:

### 1. Hardcoded Frontend Data Analysis
**Key Findings:**
- **6 files with CRITICAL hardcoded data**: All dashboards (user, seller, admin), artwork pages, profile page
- **User dashboards show identical data to all users** - multi-user functionality broken
- **Platform statistics are fake** - homepage shows hardcoded metrics
- **Business policies hardcoded in UI** - return policies, shipping times, fees in component code
- **No state persistence** - user preferences stored in useState only

**Severity Breakdown:**
- 🔴 Critical: 6 files (app-breaking issues)
- 🟡 High: 3 files (major feature degradation)
- 🟠 Medium: 2 files (maintainability issues)

### 2. API Layer & Data Pipeline Analysis
**Key Findings:**

**Backend Issues:**
- 🔴 **CRITICAL**: Auth0 client secret hardcoded in `backend/config/settings.py`
- 🔴 **CRITICAL**: `seller_id` and `bidder_id` passed as query params (can be forged)
- 🔴 **CRITICAL**: `/api/auth/me` requires `auth0_sub` query param (insecure user lookup)
- 🔴 **HIGH**: No WebSocket authentication (anyone can join rooms)
- 🔴 **HIGH**: Real-time bid events commented out (no broadcasting)
- 🔴 **HIGH**: Image upload not implemented (placeholder only)
- 🔴 **HIGH**: No auction expiration logic (auctions never end)

**Database Issues:**
- Missing indexes on foreign keys (`seller_id`, `artwork_id`, `bidder_id`)
- N+1 query problems (no eager loading)
- No pagination limits (DoS risk)
- Missing fields (`end_date` on artworks, `artist_name`, `category`)

**Frontend Integration:**
- Only 2 components use real API calls (LiveAuctions, QuickStats)
- 7+ major pages use hardcoded mock data
- WebSocket client implemented but never enabled
- No error handling for API failures

**API Completeness:** ~40% (basic endpoints exist, but missing auth, features, integration)

---

## Pre-Implementation Checklist

Before starting Stage 0, ensure:

- [ ] **Azure deployment is turned off** (or run on separate dev environment)
- [ ] **Working on `dev` branch** with latest code
- [ ] **All dependencies installed**:
  ```bash
  # Backend
  cd backend && pip install -r requirements.txt

  # Frontend
  cd frontend && npm install
  ```
- [ ] **Database is accessible** (PostgreSQL connection working)
- [ ] **Auth0 tenant is configured** (have credentials ready)
- [ ] **You have backups** of current codebase (in case rollback needed)

---

## Git Workflow & Branching Strategy

### GitFlow Convention

We will use **GitFlow** branching strategy:

```
main (production-ready code)
  └── dev (active development)
       ├── feature/stage-0-env-setup
       ├── feature/stage-1-backend-auth
       ├── feature/stage-2-db-migrations
       └── ... (one branch per stage)
```

### Workflow Per Stage

1. **Create feature branch** from `dev`:
   ```bash
   git checkout dev
   git pull origin dev
   git checkout -b feature/stage-X-descriptive-name
   ```

2. **Implement stage** (commit frequently):
   ```bash
   git add .
   git commit -m "feat: descriptive message"
   ```

3. **Merge to dev** when stage complete:
   ```bash
   git checkout dev
   git merge feature/stage-X-descriptive-name --no-ff
   git push origin dev
   ```

4. **Delete feature branch**:
   ```bash
   git branch -d feature/stage-X-descriptive-name
   ```

5. **Merge dev to main** only after ALL stages complete and tested.

### Important Notes

- ⚠️ **DO NOT modify CI/CD pipeline** without explicit user permission
- ⚠️ **DO NOT merge to `main`** until all stages complete
- ✅ **DO commit frequently** with descriptive messages
- ✅ **DO test locally** before merging to `dev`

---

## Implementation Stages

### Stage 0: Environment Security Setup 🔐
**Branch:** `feature/stage-0-env-setup`
**Priority:** CRITICAL (Must be done first)
**Estimated Context:** 20-30%

#### Goals
- Remove all hardcoded secrets from codebase
- Move sensitive configuration to environment variables
- Create `.env.example` templates for documentation
- Ensure secrets are not committed to git

#### Prerequisites
- Have Auth0 credentials ready (domain, client ID, client secret)
- Have Stripe API keys ready (if available)
- Have JWT secret key ready (generate new one if needed)

#### Tasks

**1. Backend Environment Setup**

**File:** `backend/.env.example` (CREATE)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/guesstheworth

# Auth0
AUTH0_DOMAIN=your-tenant.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-client-secret
AUTH0_AUDIENCE=https://api.guesstheworth.com

# JWT
JWT_SECRET_KEY=your-secret-key-generate-with-openssl
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...

# Application
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
ENVIRONMENT=development
```

**File:** `backend/.gitignore` (UPDATE)
```
# Add if not present:
.env
.env.local
.env.production
```

**File:** `backend/config/settings.py` (MODIFY)
- Remove ALL hardcoded values on lines 15-25
- Replace with `os.getenv()` calls with NO defaults for secrets
- Example:
  ```python
  # BEFORE (INSECURE):
  auth0_client_secret: str = "hardcoded-secret"

  # AFTER (SECURE):
  auth0_client_secret: str = os.getenv("AUTH0_CLIENT_SECRET")
  if not auth0_client_secret:
      raise ValueError("AUTH0_CLIENT_SECRET environment variable is required")
  ```
- Apply to: `auth0_client_secret`, `auth0_client_id`, `auth0_domain`, `jwt_secret_key`, `stripe_secret_key`

**File:** `backend/.env` (CREATE - do not commit)
- Copy from `.env.example`
- Fill in actual values
- Test that app starts successfully

**2. Frontend Environment Setup**

**File:** `frontend/.env.example` (CREATE)
```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_SOCKET_URL=http://localhost:8000

# Auth0 (Public - safe to expose)
VITE_AUTH0_DOMAIN=your-tenant.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_AUTH0_AUDIENCE=https://api.guesstheworth.com

# Stripe (Public key only)
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

**File:** `frontend/.gitignore` (UPDATE)
```
# Add if not present:
.env
.env.local
.env.production
```

**File:** `frontend/.env` (CREATE - do not commit)
- Copy from `.env.example`
- Fill in actual values

**3. Docker Compose Update**

**File:** `docker-compose.yml` (MODIFY)
- Update backend service to use environment variables:
  ```yaml
  backend:
    env_file:
      - ./backend/.env
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - AUTH0_CLIENT_SECRET=${AUTH0_CLIENT_SECRET}
      # ... etc
  ```

**4. Update Documentation**

**File:** `README.md` (UPDATE)
- Update "Environment Setup" section (lines 23-29)
- Add clear instructions for `.env` file creation
- List all required environment variables

#### Validation Steps
1. ✅ Start backend: `cd backend && uvicorn main:socket_app --reload`
   - Should start without errors
   - Should fail if `.env` missing
2. ✅ Start frontend: `cd frontend && npm run dev`
   - Should connect to backend
3. ✅ Verify no secrets in git: `git status` (should not show `.env` files)
4. ✅ Search codebase: `grep -r "auth0_client_secret" backend/` (should only find in settings.py with os.getenv)

#### Files Modified
- `backend/.env.example` (new)
- `backend/.env` (new, gitignored)
- `backend/.gitignore`
- `backend/config/settings.py`
- `frontend/.env.example` (new)
- `frontend/.env` (new, gitignored)
- `frontend/.gitignore`
- `docker-compose.yml`
- `README.md`

---

### Stage 1: Backend Authentication & Authorization Fixes 🔐
**Branch:** `feature/stage-1-backend-auth`
**Priority:** CRITICAL
**Estimated Context:** 40-50%

#### Goals
- Fix insecure user ID passing (extract from JWT token)
- Implement proper authentication on all endpoints
- Add ownership validation (users can only modify their own data)
- Secure WebSocket connections

#### Prerequisites
- Stage 0 complete (environment variables set up)
- Backend running and Auth0 configured

#### Tasks

**1. Create Authentication Dependency**

**File:** `backend/utils/auth.py` (MODIFY - expand existing)
- Add new function `get_current_user_from_token()`:
  ```python
  from fastapi import Depends, HTTPException, status
  from fastapi.security import HTTPBearer, HTTPAuthCredentials
  from services.auth_service import AuthService
  from database import SessionLocal

  security = HTTPBearer()

  async def get_current_user(
      credentials: HTTPAuthCredentials = Depends(security),
      db: Session = Depends(get_db)
  ):
      """
      Extract and validate user from Bearer token.
      Returns User object or raises 401.
      """
      token = credentials.credentials

      # Verify token with Auth0
      auth_service = AuthService()
      auth_user = await auth_service.verify_auth0_token(token)

      if not auth_user:
          raise HTTPException(
              status_code=status.HTTP_401_UNAUTHORIZED,
              detail="Invalid authentication credentials"
          )

      # Get user from database
      user = db.query(User).filter(User.auth0_sub == auth_user.sub).first()

      if not user:
          raise HTTPException(
              status_code=status.HTTP_404_NOT_FOUND,
              detail="User not found"
          )

      return user
  ```

**2. Fix Authentication Router**

**File:** `backend/routers/auth.py` (MODIFY)

**Change `/api/auth/me` endpoint** (lines 37-42):
```python
# BEFORE (INSECURE):
@router.get("/me", response_model=UserResponse)
async def get_current_user_endpoint(
    auth0_sub: str,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.auth0_sub == auth0_sub).first()
    # ...

# AFTER (SECURE):
@router.get("/me", response_model=UserResponse)
async def get_current_user_endpoint(
    current_user: User = Depends(get_current_user)
):
    return current_user
```

**3. Fix Artwork Router**

**File:** `backend/routers/artworks.py` (MODIFY)

**Update POST `/api/artworks/`** (lines 27-48):
```python
# BEFORE (INSECURE):
@router.post("/", response_model=ArtworkResponse)
async def create_artwork(
    seller_id: int,  # ❌ Query param - can be forged
    artwork: ArtworkCreate,
    db: Session = Depends(get_db)
):
    seller = db.query(User).filter(User.id == seller_id).first()
    # ...

# AFTER (SECURE):
@router.post("/", response_model=ArtworkResponse)
async def create_artwork(
    artwork: ArtworkCreate,
    current_user: User = Depends(require_seller),  # ✅ From token
    db: Session = Depends(get_db)
):
    # Verify user is seller or admin
    if current_user.role not in [UserRole.SELLER, UserRole.ADMIN]:
        raise HTTPException(status_code=403, detail="Only sellers can create artworks")

    db_artwork = Artwork(
        **artwork.dict(),
        seller_id=current_user.id  # ✅ Use authenticated user's ID
    )
    db.add(db_artwork)
    db.commit()
    db.refresh(db_artwork)
    return db_artwork
```

**Add new endpoint: GET `/api/artworks/my-artworks`** (for seller dashboard):
```python
@router.get("/my-artworks", response_model=List[ArtworkWithSecretResponse])
async def get_my_artworks(
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db)
):
    """Get all artworks owned by the authenticated seller."""
    artworks = db.query(Artwork).filter(
        Artwork.seller_id == current_user.id
    ).all()
    return artworks
```

**4. Fix Bid Router**

**File:** `backend/routers/bids.py` (MODIFY)

**Update POST `/api/bids/`** (lines 19-69):
```python
# BEFORE (INSECURE):
@router.post("/", response_model=BidResponse)
async def create_bid(
    bidder_id: int,  # ❌ Query param - can be forged
    bid: BidCreate,
    db: Session = Depends(get_db)
):
    bidder = db.query(User).filter(User.id == bidder_id).first()
    # ...

# AFTER (SECURE):
@router.post("/", response_model=BidResponse)
async def create_bid(
    bid: BidCreate,
    current_user: User = Depends(require_buyer),  # ✅ From token
    db: Session = Depends(get_db)
):
    # Get artwork
    artwork = db.query(Artwork).filter(Artwork.id == bid.artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    if artwork.status != ArtworkStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Artwork is not active")

    # Prevent seller from bidding on own artwork
    if artwork.seller_id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot bid on your own artwork"
        )

    # Create bid with authenticated user's ID
    db_bid = Bid(
        artwork_id=bid.artwork_id,
        bidder_id=current_user.id,  # ✅ Use authenticated user's ID
        amount=bid.amount,
        is_winning=(bid.amount >= artwork.secret_threshold)
    )

    # Update artwork if winning
    if db_bid.is_winning:
        artwork.status = ArtworkStatus.SOLD
        artwork.current_highest_bid = bid.amount
    elif bid.amount > artwork.current_highest_bid:
        artwork.current_highest_bid = bid.amount

    db.add(db_bid)
    db.commit()
    db.refresh(db_bid)

    return db_bid
```

**Add new endpoint: GET `/api/bids/my-bids`**:
```python
@router.get("/my-bids", response_model=List[BidResponse])
async def get_my_bids(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all bids placed by the authenticated user."""
    bids = db.query(Bid).filter(
        Bid.bidder_id == current_user.id
    ).order_by(Bid.bid_time.desc()).all()
    return bids
```

**5. Secure WebSocket Connections**

**File:** `backend/main.py` (MODIFY - lines 55-76)

**Update connect event handler**:
```python
from services.jwt_service import JWTService

@sio.event
async def connect(sid, environ):
    """Authenticate WebSocket connection."""
    # Extract token from query params
    query_string = environ.get('QUERY_STRING', '')
    params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
    token = params.get('token')

    if not token:
        print(f"Connection rejected: No token provided")
        return False

    try:
        # Verify JWT token
        jwt_service = JWTService()
        payload = jwt_service.verify_token(token)
        auth0_sub = payload.get('sub')

        # Store user info in session
        await sio.save_session(sid, {'auth0_sub': auth0_sub, 'authenticated': True})
        print(f"Client {sid} connected (authenticated as {auth0_sub})")
        return True

    except Exception as e:
        print(f"Connection rejected: Invalid token - {e}")
        return False

@sio.event
async def join_artwork(sid, data):
    """Join artwork room (authenticated users only)."""
    session = await sio.get_session(sid)
    if not session.get('authenticated'):
        return {'error': 'Not authenticated'}

    artwork_id = data.get('artwork_id')
    sio.enter_room(sid, f"artwork_{artwork_id}")
    print(f"Client {sid} joined room artwork_{artwork_id}")
    return {'status': 'joined', 'room': f"artwork_{artwork_id}"}
```

**6. Protect Existing Endpoints**

Add authentication to endpoints that don't have it:

**File:** `backend/routers/users.py` (MODIFY)
- `GET /api/users/` - Add `Depends(require_admin)` (only admins can list users)
- `GET /api/users/{user_id}` - Add `Depends(get_current_user)` (authenticated users only)

**File:** `backend/routers/artworks.py` (MODIFY)
- `GET /api/artworks/` - Keep public (no auth required)
- `GET /api/artworks/{id}` - Keep public
- `POST /api/artworks/{id}/upload-image` - Add `Depends(get_current_user)` + ownership validation

#### Validation Steps
1. ✅ **Test user registration**: Register new user via Auth0 login flow
2. ✅ **Test GET `/api/auth/me`**:
   - Without token → 401 Unauthorized
   - With valid token → Returns user object
3. ✅ **Test POST `/api/artworks/`**:
   - Without token → 401
   - With buyer token → 403 Forbidden
   - With seller token → Creates artwork with correct seller_id
   - Verify seller_id matches authenticated user (not forged)
4. ✅ **Test POST `/api/bids/`**:
   - Without token → 401
   - With valid token → Creates bid with correct bidder_id
   - Seller bidding on own artwork → 400 error
5. ✅ **Test WebSocket connection**:
   - Connect without token → Connection rejected
   - Connect with valid token → Success
   - Join room without auth → Error

#### Files Modified
- `backend/utils/auth.py`
- `backend/routers/auth.py`
- `backend/routers/artworks.py`
- `backend/routers/bids.py`
- `backend/routers/users.py`
- `backend/main.py`

---

### Stage 2: Database Schema Improvements & Migrations 🗄️
**Branch:** `feature/stage-2-db-migrations`
**Priority:** HIGH
**Estimated Context:** 30-40%

#### Goals
- Add missing fields to database models (auction expiration, artist name, category)
- Add database indexes for performance
- Create Alembic migrations for all changes
- Apply migrations to database

#### Prerequisites
- Stage 1 complete (auth fixes done)
- Database accessible
- Alembic configured

#### Tasks

**1. Update Artwork Model**

**File:** `backend/models/artwork.py` (MODIFY)

Add new fields:
```python
class Artwork(Base):
    __tablename__ = "artworks"

    # ... existing fields ...

    # NEW FIELDS:
    artist_name = Column(String, nullable=True)
    category = Column(String, nullable=True)
    end_date = Column(DateTime, nullable=True)  # When auction ends

    # Add index to seller_id
    __table_args__ = (
        Index('idx_artwork_seller_id', 'seller_id'),
        Index('idx_artwork_status', 'status'),
        Index('idx_artwork_end_date', 'end_date'),
    )
```

**2. Update Bid Model**

**File:** `backend/models/bid.py` (MODIFY)

Add indexes:
```python
class Bid(Base):
    __tablename__ = "bids"

    # ... existing fields ...

    __table_args__ = (
        Index('idx_bid_artwork_id', 'artwork_id'),
        Index('idx_bid_bidder_id', 'bidder_id'),
        Index('idx_bid_time', 'bid_time'),
    )
```

**3. Update Artwork Schemas**

**File:** `backend/schemas/artwork.py` (MODIFY)

Update schemas to include new fields:
```python
class ArtworkBase(BaseModel):
    title: str
    description: Optional[str] = None
    artist_name: Optional[str] = None  # NEW
    category: Optional[str] = None     # NEW
    end_date: Optional[datetime] = None  # NEW

class ArtworkCreate(ArtworkBase):
    secret_threshold: float

class ArtworkResponse(ArtworkBase):
    id: int
    seller_id: int
    current_highest_bid: float
    image_url: Optional[str]
    status: ArtworkStatus
    created_at: datetime
    # Note: secret_threshold NOT included (hidden from buyers)

class ArtworkWithSecretResponse(ArtworkResponse):
    secret_threshold: float  # Only visible to seller
```

**4. Create Alembic Migration**

Generate migration:
```bash
cd backend
alembic revision --autogenerate -m "Add artwork fields and indexes"
```

Review generated migration file in `backend/alembic/versions/XXXX_add_artwork_fields_and_indexes.py`:
- Verify it adds columns: `artist_name`, `category`, `end_date`
- Verify it creates indexes on: `seller_id`, `status`, `end_date`, `artwork_id`, `bidder_id`, `bid_time`

**5. Apply Migration**

```bash
cd backend
alembic upgrade head
```

Verify migration applied:
```bash
# In PostgreSQL
\d artworks
\d bids
\di  # List indexes
```

**6. Update Docker Compose**

**File:** `docker-compose.yml` (MODIFY)

Ensure backend runs migrations on startup:
```yaml
backend:
  command: >
    sh -c "alembic upgrade head &&
           uvicorn main:socket_app --host 0.0.0.0 --port 8000 --reload"
```

#### Validation Steps
1. ✅ **Check migration applied**: `alembic current` should show latest revision
2. ✅ **Verify new columns exist**: Query database to check `artworks` table has new fields
3. ✅ **Verify indexes created**: Check `\di` in PostgreSQL shows new indexes
4. ✅ **Test creating artwork with new fields**:
   ```bash
   curl -X POST http://localhost:8000/api/artworks/ \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Test Art",
       "artist_name": "Test Artist",
       "category": "Painting",
       "end_date": "2025-02-01T00:00:00",
       "secret_threshold": 100.0
     }'
   ```
5. ✅ **Test rollback**: `alembic downgrade -1` then `alembic upgrade head`

#### Files Modified
- `backend/models/artwork.py`
- `backend/models/bid.py`
- `backend/schemas/artwork.py`
- `backend/alembic/versions/XXXX_add_artwork_fields_and_indexes.py` (new)
- `docker-compose.yml`

---

### Stage 3: Frontend API Integration - Core CRUD 🔌
**Branch:** `feature/stage-3-frontend-crud-integration`
**Priority:** CRITICAL
**Estimated Context:** 50-60%

#### Goals
- Replace hardcoded artwork data with real API calls
- Implement authentication in frontend API client
- Connect artwork listing, detail, and creation pages to backend
- Update Auth0 integration to work with new `/api/auth/me` endpoint

#### Prerequisites
- Stage 1 complete (backend auth fixed)
- Stage 2 complete (database updated)
- Frontend running and connected to backend

#### Tasks

**1. Update API Client for Authentication**

**File:** `frontend/src/services/api.js` (MODIFY)

Update `get_current_user` to use token instead of auth0_sub:
```javascript
// BEFORE:
getCurrentUser(auth0Sub) {
  return api.get(`/auth/me?auth0_sub=${auth0Sub}`);
}

// AFTER:
getCurrentUser() {
  // Token automatically added by interceptor
  return api.get('/auth/me');
}
```

Add seller-specific methods:
```javascript
artworkService: {
  // ... existing methods ...

  getMyArtworks() {
    return api.get('/artworks/my-artworks');
  },
},

bidService: {
  // ... existing methods ...

  getMyBids() {
    return api.get('/bids/my-bids');
  },
},
```

**2. Fix Auth0 Integration**

**File:** `frontend/src/auth/AuthCallback.jsx` or wherever Auth0 callback is handled

Update to call new `/api/auth/me` endpoint:
```javascript
// After Auth0 login success:
const { accessToken } = await getAccessTokenSilently();

// Store token
localStorage.setItem('access_token', accessToken);

// Get user from backend (no auth0_sub needed)
const user = await userService.getCurrentUser();

// Update auth store
useAuthStore.getState().setAuth(user, accessToken);
```

**3. Update ArtworksPage to Use Real API**

**File:** `frontend/src/pages/ArtworksPage.jsx` (MODIFY)

**Replace hardcoded mock data** (lines 23-96) with React Query:
```javascript
import { useQuery } from '@tanstack/react-query';
import { artworkService } from '../services/api';

function ArtworksPage() {
  const [filters, setFilters] = useState({
    category: 'all',
    searchTerm: '',
    sortBy: 'ending-soon',
  });

  // Fetch artworks from API
  const { data: artworks = [], isLoading, error } = useQuery({
    queryKey: ['artworks', filters],
    queryFn: () => artworkService.getAll({
      // Apply filters as query params
      category: filters.category !== 'all' ? filters.category : undefined,
      search: filters.searchTerm || undefined,
      sort: filters.sortBy,
    }),
    staleTime: 30000, // 30 seconds
  });

  if (isLoading) return <Spinner />;
  if (error) return <Text>Error loading artworks: {error.message}</Text>;

  // Client-side filtering if needed (or move to backend)
  const filteredArtworks = artworks.filter(artwork => {
    const matchesSearch = !filters.searchTerm ||
      artwork.title.toLowerCase().includes(filters.searchTerm.toLowerCase());
    const matchesCategory = filters.category === 'all' ||
      artwork.category === filters.category;
    return matchesSearch && matchesCategory;
  });

  // Render artworks
  return (
    <Box>
      {/* Filter UI */}
      {/* ... */}

      {/* Artwork Grid */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={6}>
        {filteredArtworks.map(artwork => (
          <ArtworkCard key={artwork.id} artwork={artwork} />
        ))}
      </SimpleGrid>
    </Box>
  );
}
```

**Update categories** (line 122) to be dynamic:
```javascript
// Fetch unique categories from artworks
const categories = ['all', ...new Set(artworks.map(a => a.category).filter(Boolean))];
```

**4. Update ArtworkPage to Use Real API**

**File:** `frontend/src/pages/ArtworkPage.jsx` (MODIFY)

**Replace hardcoded data** (lines 26-54) with React Query:
```javascript
import { useQuery } from '@tanstack/react-query';
import { useParams } from 'react-router-dom';
import { artworkService, bidService } from '../services/api';

function ArtworkPage() {
  const { id } = useParams();

  // Fetch artwork details
  const { data: artwork, isLoading: artworkLoading } = useQuery({
    queryKey: ['artwork', id],
    queryFn: () => artworkService.getById(id),
    staleTime: 10000,
  });

  // Fetch recent bids
  const { data: recentBids = [], isLoading: bidsLoading } = useQuery({
    queryKey: ['bids', id],
    queryFn: () => bidService.getByArtwork(id),
    staleTime: 5000,
  });

  if (artworkLoading || bidsLoading) return <Spinner />;
  if (!artwork) return <Text>Artwork not found</Text>;

  return (
    <Box>
      <Heading>{artwork.title}</Heading>
      <Text>By {artwork.artist_name || 'Unknown Artist'}</Text>
      <Text>{artwork.description}</Text>

      {/* Display artwork details */}
      <Text>Current Bid: ${artwork.current_highest_bid}</Text>
      <Text>Status: {artwork.status}</Text>

      {/* Bid Form */}
      <BidForm artworkId={id} />

      {/* Recent Bids */}
      <Box>
        <Heading size="md">Recent Bids</Heading>
        {recentBids.map(bid => (
          <Box key={bid.id}>
            <Text>${bid.amount} - {new Date(bid.bid_time).toLocaleString()}</Text>
          </Box>
        ))}
      </Box>
    </Box>
  );
}
```

**5. Create BidForm Component**

**File:** `frontend/src/components/BidForm.jsx` (CREATE NEW)

```javascript
import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { Box, Input, Button, useToast, FormControl, FormLabel } from '@chakra-ui/react';
import { bidService } from '../services/api';
import useAuthStore from '../store/authStore';

export default function BidForm({ artworkId }) {
  const [bidAmount, setBidAmount] = useState('');
  const { isAuthenticated } = useAuthStore();
  const toast = useToast();
  const queryClient = useQueryClient();

  const placeBidMutation = useMutation({
    mutationFn: (amount) => bidService.create({
      artwork_id: parseInt(artworkId),
      amount: parseFloat(amount),
    }),
    onSuccess: (data) => {
      toast({
        title: data.is_winning ? 'Congratulations! You won!' : 'Bid placed successfully',
        status: data.is_winning ? 'success' : 'info',
        duration: 5000,
      });

      // Refresh artwork and bids
      queryClient.invalidateQueries(['artwork', artworkId]);
      queryClient.invalidateQueries(['bids', artworkId]);

      setBidAmount('');
    },
    onError: (error) => {
      toast({
        title: 'Bid failed',
        description: error.response?.data?.detail || error.message,
        status: 'error',
        duration: 5000,
      });
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!bidAmount || parseFloat(bidAmount) <= 0) {
      toast({ title: 'Please enter a valid bid amount', status: 'warning' });
      return;
    }
    placeBidMutation.mutate(bidAmount);
  };

  if (!isAuthenticated) {
    return <Text>Please log in to place a bid</Text>;
  }

  return (
    <Box as="form" onSubmit={handleSubmit}>
      <FormControl>
        <FormLabel>Your Bid</FormLabel>
        <Input
          type="number"
          step="0.01"
          value={bidAmount}
          onChange={(e) => setBidAmount(e.target.value)}
          placeholder="Enter bid amount"
        />
      </FormControl>
      <Button
        type="submit"
        mt={4}
        isLoading={placeBidMutation.isLoading}
      >
        Place Bid
      </Button>
    </Box>
  );
}
```

**6. Update AddArtworkPage**

**File:** `frontend/src/pages/AddArtworkPage.jsx` (MODIFY)

**Connect form to API** (replace TODO at line 20):
```javascript
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { artworkService } from '../services/api';
import useAuthStore from '../store/authStore';

function AddArtworkPage() {
  const navigate = useNavigate();
  const toast = useToast();
  const queryClient = useQueryClient();
  const { isSeller, isAdmin } = useAuthStore();

  // Redirect if not seller
  if (!isSeller() && !isAdmin()) {
    return <Text>You must be a seller to create artworks</Text>;
  }

  const createArtworkMutation = useMutation({
    mutationFn: (artworkData) => artworkService.create(artworkData),
    onSuccess: (data) => {
      toast({
        title: 'Artwork created successfully',
        status: 'success',
      });
      queryClient.invalidateQueries(['artworks']);
      navigate(`/artworks/${data.id}`);
    },
    onError: (error) => {
      toast({
        title: 'Failed to create artwork',
        description: error.response?.data?.detail || error.message,
        status: 'error',
      });
    },
  });

  const handleSubmit = (formData) => {
    createArtworkMutation.mutate({
      title: formData.title,
      description: formData.description,
      artist_name: formData.artist_name,
      category: formData.category,
      secret_threshold: parseFloat(formData.secret_threshold),
      end_date: formData.end_date ? new Date(formData.end_date).toISOString() : null,
    });
  };

  return (
    <Box>
      <Heading>Create New Artwork</Heading>
      <ArtworkForm
        onSubmit={handleSubmit}
        isLoading={createArtworkMutation.isLoading}
      />
    </Box>
  );
}
```

**7. Update QuickStats to Remove Fallback Mock Data**

**File:** `frontend/src/components/home/QuickStats.jsx` (MODIFY)

Remove hardcoded fallback stats (lines 12-17) and show error message instead:
```javascript
const { data: platformStats, isLoading, error } = useQuery({
  queryKey: ["platform-stats"],
  queryFn: statsService.getPlatformStats,
  staleTime: 5 * 60 * 1000,
  retry: 2,
});

if (error) {
  return <Text color="red.500">Unable to load platform statistics</Text>;
}

// Use real data only (no fallback)
```

#### Validation Steps
1. ✅ **Test artwork listing page**:
   - Visit `/artworks`
   - Should load real artworks from database
   - Filter by category should work
   - Search should work
2. ✅ **Test artwork detail page**:
   - Click on artwork card
   - Should show real artwork details
   - Should show recent bids
3. ✅ **Test placing bid**:
   - Log in as buyer
   - Enter bid amount
   - Submit bid
   - Should see success message
   - Bid should appear in recent bids
4. ✅ **Test creating artwork**:
   - Log in as seller
   - Fill out artwork form
   - Submit
   - Should redirect to new artwork page
   - Artwork should appear in listing
5. ✅ **Test authentication**:
   - Try accessing protected pages without login → Redirect to login
   - Try placing bid without login → Show error message

#### Files Modified
- `frontend/src/services/api.js`
- `frontend/src/pages/ArtworksPage.jsx`
- `frontend/src/pages/ArtworkPage.jsx`
- `frontend/src/pages/AddArtworkPage.jsx`
- `frontend/src/components/BidForm.jsx` (new)
- `frontend/src/components/home/QuickStats.jsx`
- `frontend/src/auth/AuthCallback.jsx` (or wherever Auth0 callback is)

---

### Stage 4: Backend API Completion - Missing Endpoints 🔧
**Branch:** `feature/stage-4-backend-api-completion`
**Priority:** MEDIUM
**Estimated Context:** 30-40%

#### Goals
- Implement missing CRUD operations (update, delete)
- Add endpoints for dashboard data (user stats, seller analytics)
- Implement image upload functionality
- Add auction expiration logic

#### Prerequisites
- Stage 2 complete (database schema updated)
- Stage 3 complete (basic frontend integration working)

#### Tasks

**1. Add User Update Endpoint**

**File:** `backend/routers/users.py` (ADD)

```python
@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile."""
    for field, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)
    return current_user
```

**2. Add Artwork Update/Delete Endpoints**

**File:** `backend/routers/artworks.py` (ADD)

```python
@router.put("/{artwork_id}", response_model=ArtworkResponse)
async def update_artwork(
    artwork_id: int,
    artwork_update: ArtworkUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update artwork (only owner or admin)."""
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    # Check ownership
    if artwork.seller_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Update fields
    for field, value in artwork_update.dict(exclude_unset=True).items():
        setattr(artwork, field, value)

    db.commit()
    db.refresh(artwork)
    return artwork

@router.delete("/{artwork_id}")
async def delete_artwork(
    artwork_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete artwork (only owner or admin)."""
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    # Check ownership
    if artwork.seller_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if artwork has bids
    if artwork.status == ArtworkStatus.SOLD:
        raise HTTPException(status_code=400, detail="Cannot delete sold artwork")

    db.delete(artwork)
    db.commit()
    return {"message": "Artwork deleted successfully"}
```

**3. Implement Image Upload**

**File:** `backend/routers/artworks.py` (MODIFY lines 51-59)

```python
import os
import uuid
from fastapi import UploadFile, File
from PIL import Image

@router.post("/{artwork_id}/upload-image")
async def upload_artwork_image(
    artwork_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload artwork image (only owner or admin)."""
    artwork = db.query(Artwork).filter(Artwork.id == artwork_id).first()
    if not artwork:
        raise HTTPException(status_code=404, detail="Artwork not found")

    # Check ownership
    if artwork.seller_id != current_user.id and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Validate file size (max 5MB)
    MAX_SIZE = 5 * 1024 * 1024
    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 5MB)")

    # Generate unique filename
    file_extension = file.filename.split('.')[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"

    # Save to uploads directory
    upload_dir = "uploads/artworks"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, unique_filename)

    # Save file
    with open(file_path, 'wb') as f:
        f.write(contents)

    # Optional: Resize/optimize image with Pillow
    try:
        img = Image.open(file_path)
        img.thumbnail((1200, 1200))
        img.save(file_path, optimize=True, quality=85)
    except Exception as e:
        print(f"Image optimization failed: {e}")

    # Update artwork with image URL
    artwork.image_url = f"/uploads/artworks/{unique_filename}"
    db.commit()

    return {"message": "Image uploaded successfully", "image_url": artwork.image_url}
```

**Add static file serving** in `backend/main.py`:
```python
from fastapi.staticfiles import StaticFiles

# Add after app initialization
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
```

**4. Add Dashboard Stats Endpoints**

**File:** `backend/routers/stats.py` (CREATE NEW)

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.user import User
from models.artwork import Artwork, ArtworkStatus
from models.bid import Bid
from utils.auth import get_current_user

router = APIRouter(prefix="/api/stats", tags=["stats"])

@router.get("/user")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's statistics."""
    # Count active bids
    active_bids = db.query(Bid).join(Artwork).filter(
        Bid.bidder_id == current_user.id,
        Artwork.status == ArtworkStatus.ACTIVE
    ).count()

    # Count won auctions
    won_auctions = db.query(Bid).join(Artwork).filter(
        Bid.bidder_id == current_user.id,
        Bid.is_winning == True,
        Artwork.status == ArtworkStatus.SOLD
    ).count()

    # Calculate total spent
    total_spent = db.query(func.sum(Bid.amount)).join(Artwork).filter(
        Bid.bidder_id == current_user.id,
        Bid.is_winning == True,
        Artwork.status == ArtworkStatus.SOLD
    ).scalar() or 0

    # Count watchlist (if favorites implemented)
    watchlist = 0  # TODO: Implement when favorites are in database

    return {
        "active_bids": active_bids,
        "won_auctions": won_auctions,
        "total_spent": float(total_spent),
        "watchlist": watchlist,
    }

@router.get("/seller")
async def get_seller_stats(
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db)
):
    """Get seller statistics."""
    # Count artworks by status
    total_artworks = db.query(Artwork).filter(
        Artwork.seller_id == current_user.id
    ).count()

    active_auctions = db.query(Artwork).filter(
        Artwork.seller_id == current_user.id,
        Artwork.status == ArtworkStatus.ACTIVE
    ).count()

    sold_artworks = db.query(Artwork).filter(
        Artwork.seller_id == current_user.id,
        Artwork.status == ArtworkStatus.SOLD
    ).count()

    # Calculate total earnings
    total_earnings = db.query(func.sum(Artwork.current_highest_bid)).filter(
        Artwork.seller_id == current_user.id,
        Artwork.status == ArtworkStatus.SOLD
    ).scalar() or 0

    return {
        "total_artworks": total_artworks,
        "active_auctions": active_auctions,
        "sold_artworks": sold_artworks,
        "total_earnings": float(total_earnings),
    }

@router.get("/platform")
async def get_platform_stats(db: Session = Depends(get_db)):
    """Get public platform statistics."""
    total_artworks = db.query(Artwork).count()
    total_users = db.query(User).count()
    total_bids = db.query(Bid).count()
    active_auctions = db.query(Artwork).filter(
        Artwork.status == ArtworkStatus.ACTIVE
    ).count()

    return {
        "total_artworks": total_artworks,
        "total_users": total_users,
        "total_bids": total_bids,
        "active_auctions": active_auctions,
    }
```

**Register stats router** in `backend/main.py`:
```python
from routers import stats

app.include_router(stats.router)
```

**5. Add Auction Expiration Logic**

**File:** `backend/services/auction_service.py` (CREATE NEW)

```python
from datetime import datetime
from sqlalchemy.orm import Session
from models.artwork import Artwork, ArtworkStatus
from models.bid import Bid

class AuctionService:
    @staticmethod
    def check_expired_auctions(db: Session):
        """Check and close expired auctions."""
        now = datetime.utcnow()

        # Find active artworks past end_date
        expired_artworks = db.query(Artwork).filter(
            Artwork.status == ArtworkStatus.ACTIVE,
            Artwork.end_date < now
        ).all()

        for artwork in expired_artworks:
            # Find winning bid
            winning_bid = db.query(Bid).filter(
                Bid.artwork_id == artwork.id,
                Bid.is_winning == True
            ).first()

            if winning_bid:
                # Mark as sold
                artwork.status = ArtworkStatus.SOLD
            else:
                # No winner, archive
                artwork.status = ArtworkStatus.ARCHIVED

        db.commit()
        return len(expired_artworks)
```

**File:** `backend/routers/artworks.py` (ADD endpoint)

```python
from services.auction_service import AuctionService

@router.post("/expire-auctions")
async def expire_auctions(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Manually trigger auction expiration check (admin only)."""
    count = AuctionService.check_expired_auctions(db)
    return {"message": f"Closed {count} expired auctions"}
```

**Note:** For automatic expiration, you would need a background task (Celery, APScheduler, etc.). This is out of scope for now - manual trigger endpoint is sufficient.

#### Validation Steps
1. ✅ **Test user update**: `PUT /api/users/me` with updated name
2. ✅ **Test artwork update**: `PUT /api/artworks/{id}` with new description
3. ✅ **Test artwork delete**: `DELETE /api/artworks/{id}` (verify ownership check)
4. ✅ **Test image upload**:
   - Upload valid image (JPEG, PNG)
   - Try invalid file type → 400 error
   - Try file > 5MB → 400 error
   - Verify image saved to `uploads/artworks/`
5. ✅ **Test stats endpoints**:
   - `GET /api/stats/user` → Returns user stats
   - `GET /api/stats/seller` → Returns seller stats (requires seller role)
   - `GET /api/stats/platform` → Returns platform stats (public)
6. ✅ **Test auction expiration**:
   - Create artwork with end_date in past
   - Call `POST /api/artworks/expire-auctions`
   - Verify artwork status changes to SOLD or ARCHIVED

#### Files Modified
- `backend/routers/users.py`
- `backend/routers/artworks.py`
- `backend/routers/stats.py` (new)
- `backend/services/auction_service.py` (new)
- `backend/main.py`

---

### Stage 5: Frontend Dashboard Integration 📊
**Branch:** `feature/stage-5-frontend-dashboards`
**Priority:** HIGH
**Estimated Context:** 50-60%

#### Goals
- Replace hardcoded dashboard data with real API calls
- Connect UserDashboard, SellerDashboard, and ProfilePage to backend
- Implement user stats display
- Add user profile editing functionality

#### Prerequisites
- Stage 3 complete (core CRUD integrated)
- Stage 4 complete (stats endpoints available)

#### Tasks

**1. Update API Service with Stats Methods**

**File:** `frontend/src/services/api.js` (ADD)

```javascript
statsService: {
  getPlatformStats() {
    return api.get('/stats/platform');
  },

  getUserStats() {
    return api.get('/stats/user');
  },

  getSellerStats() {
    return api.get('/stats/seller');
  },
},
```

**2. Update UserDashboard**

**File:** `frontend/src/pages/UserDashboard.jsx` (MODIFY - replace lines 20-83)

```javascript
import { useQuery } from '@tanstack/react-query';
import { statsService, bidService } from '../services/api';

function UserDashboard() {
  // Fetch user stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['user-stats'],
    queryFn: statsService.getUserStats,
    staleTime: 30000,
  });

  // Fetch user's bids
  const { data: myBids = [], isLoading: bidsLoading } = useQuery({
    queryKey: ['my-bids'],
    queryFn: bidService.getMyBids,
    staleTime: 10000,
  });

  if (statsLoading || bidsLoading) return <Spinner />;

  // Separate active bids and won auctions
  const activeBids = myBids.filter(bid => bid.artwork?.status === 'ACTIVE');
  const wonAuctions = myBids.filter(bid => bid.is_winning && bid.artwork?.status === 'SOLD');

  return (
    <Box>
      {/* Stats Cards */}
      <SimpleGrid columns={{ base: 1, md: 4 }} spacing={6} mb={8}>
        <StatCard label="Active Bids" value={stats.active_bids} icon="💰" />
        <StatCard label="Won Auctions" value={stats.won_auctions} icon="🏆" />
        <StatCard label="Total Spent" value={`$${stats.total_spent}`} icon="💵" />
        <StatCard label="Watchlist" value={stats.watchlist} icon="❤️" />
      </SimpleGrid>

      {/* Active Bids Section */}
      <Box mb={8}>
        <Heading size="md" mb={4}>Active Bids</Heading>
        {activeBids.length === 0 ? (
          <Text>No active bids</Text>
        ) : (
          activeBids.map(bid => (
            <BidCard key={bid.id} bid={bid} />
          ))
        )}
      </Box>

      {/* Won Auctions Section */}
      <Box>
        <Heading size="md" mb={4}>Won Auctions</Heading>
        {wonAuctions.length === 0 ? (
          <Text>No won auctions yet</Text>
        ) : (
          wonAuctions.map(bid => (
            <WonAuctionCard key={bid.id} bid={bid} />
          ))
        )}
      </Box>
    </Box>
  );
}
```

**3. Update SellerDashboard**

**File:** `frontend/src/pages/SellerDashboard.jsx` (MODIFY - replace lines 20-402)

```javascript
import { useQuery } from '@tanstack/react-query';
import { statsService, artworkService } from '../services/api';

function SellerDashboard() {
  // Fetch seller stats
  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['seller-stats'],
    queryFn: statsService.getSellerStats,
    staleTime: 30000,
  });

  // Fetch seller's artworks
  const { data: myArtworks = [], isLoading: artworksLoading } = useQuery({
    queryKey: ['my-artworks'],
    queryFn: artworkService.getMyArtworks,
    staleTime: 10000,
  });

  if (statsLoading || artworksLoading) return <Spinner />;

  // Separate by status
  const activeArtworks = myArtworks.filter(a => a.status === 'ACTIVE');
  const soldArtworks = myArtworks.filter(a => a.status === 'SOLD');

  return (
    <Box>
      {/* Stats Cards */}
      <SimpleGrid columns={{ base: 1, md: 4 }} spacing={6} mb={8}>
        <StatCard label="Total Artworks" value={stats.total_artworks} />
        <StatCard label="Active Auctions" value={stats.active_auctions} />
        <StatCard label="Sold" value={stats.sold_artworks} />
        <StatCard label="Total Earnings" value={`$${stats.total_earnings}`} />
      </SimpleGrid>

      {/* Active Artworks */}
      <Box mb={8}>
        <Heading size="md" mb={4}>Active Artworks</Heading>
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
          {activeArtworks.map(artwork => (
            <SellerArtworkCard key={artwork.id} artwork={artwork} />
          ))}
        </SimpleGrid>
      </Box>

      {/* Sales History */}
      <Box>
        <Heading size="md" mb={4}>Sales History</Heading>
        {soldArtworks.map(artwork => (
          <SaleCard key={artwork.id} artwork={artwork} />
        ))}
      </Box>
    </Box>
  );
}
```

**Note:** `SellerArtworkCard` should display `secret_threshold` since seller owns the artwork and backend returns `ArtworkWithSecretResponse`.

**4. Update ProfilePage**

**File:** `frontend/src/pages/ProfilePage.jsx` (MODIFY - replace lines 26-70)

```javascript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { userService, statsService } from '../services/api';
import useAuthStore from '../store/authStore';

function ProfilePage() {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const toast = useToast();

  // Fetch current user data
  const { data: currentUser, isLoading } = useQuery({
    queryKey: ['current-user'],
    queryFn: userService.getCurrentUser,
    staleTime: 60000,
  });

  // Fetch user stats
  const { data: userStats } = useQuery({
    queryKey: ['user-stats'],
    queryFn: statsService.getUserStats,
  });

  // Update user mutation
  const updateUserMutation = useMutation({
    mutationFn: (userData) => userService.updateProfile(userData),
    onSuccess: () => {
      toast({ title: 'Profile updated successfully', status: 'success' });
      queryClient.invalidateQueries(['current-user']);
    },
    onError: (error) => {
      toast({
        title: 'Update failed',
        description: error.message,
        status: 'error'
      });
    },
  });

  if (isLoading) return <Spinner />;

  return (
    <Box>
      {/* Profile Header */}
      <Heading>{currentUser.name}</Heading>
      <Text>{currentUser.email}</Text>
      <Badge>{currentUser.role}</Badge>

      {/* Stats Grid */}
      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4} my={6}>
        <StatCard label="Total Bids" value={userStats?.active_bids || 0} />
        <StatCard label="Won Auctions" value={userStats?.won_auctions || 0} />
        <StatCard label="Member Since" value={new Date(currentUser.created_at).toLocaleDateString()} />
      </SimpleGrid>

      {/* Edit Profile Form */}
      <ProfileEditForm
        user={currentUser}
        onSubmit={updateUserMutation.mutate}
        isLoading={updateUserMutation.isLoading}
      />
    </Box>
  );
}
```

**5. Add Update Profile Method to API Service**

**File:** `frontend/src/services/api.js` (ADD)

```javascript
userService: {
  // ... existing methods ...

  updateProfile(userData) {
    return api.put('/users/me', userData);
  },
},
```

**6. Update QuickStats Component**

**File:** `frontend/src/components/home/QuickStats.jsx` (MODIFY)

Replace hardcoded personal stats (lines 19-24) with real data:
```javascript
import { useQuery } from '@tanstack/react-query';
import { statsService } from '../../services/api';
import useAuthStore from '../../store/authStore';

function QuickStats() {
  const { isAuthenticated } = useAuthStore();

  // Fetch user stats (only if logged in)
  const { data: userStats } = useQuery({
    queryKey: ['user-stats'],
    queryFn: statsService.getUserStats,
    enabled: isAuthenticated,
    staleTime: 60000,
  });

  // Fetch platform stats
  const { data: platformStats } = useQuery({
    queryKey: ['platform-stats'],
    queryFn: statsService.getPlatformStats,
    staleTime: 5 * 60 * 1000,
  });

  const personalStats = isAuthenticated ? [
    { label: "Your Bids", value: userStats?.active_bids || 0, icon: "💰" },
    { label: "Artworks Won", value: userStats?.won_auctions || 0, icon: "🏆" },
    { label: "Following", value: 0, icon: "👥" },  // TODO: Implement follows
    { label: "Wishlist", value: userStats?.watchlist || 0, icon: "❤️" },
  ] : [];

  return (
    <Box>
      {isAuthenticated && (
        <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4} mb={6}>
          {personalStats.map(stat => (
            <StatCard key={stat.label} {...stat} />
          ))}
        </SimpleGrid>
      )}

      {/* Platform Stats */}
      <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
        <StatCard label="Total Artworks" value={platformStats?.total_artworks || 0} />
        <StatCard label="Total Bids" value={platformStats?.total_bids || 0} />
        <StatCard label="Active Auctions" value={platformStats?.active_auctions || 0} />
        <StatCard label="Total Users" value={platformStats?.total_users || 0} />
      </SimpleGrid>
    </Box>
  );
}
```

#### Validation Steps
1. ✅ **Test UserDashboard**:
   - Should load user stats from API
   - Should display user's bids
   - Should show won auctions
2. ✅ **Test SellerDashboard**:
   - Should load seller stats
   - Should display seller's artworks with secret thresholds visible
   - Should show sales history
3. ✅ **Test ProfilePage**:
   - Should display current user info
   - Should allow editing profile
   - Update should persist to database
4. ✅ **Test QuickStats**:
   - Logged-out users see platform stats only
   - Logged-in users see personal + platform stats
   - Stats update when user places bids/wins auctions

#### Files Modified
- `frontend/src/services/api.js`
- `frontend/src/pages/UserDashboard.jsx`
- `frontend/src/pages/SellerDashboard.jsx`
- `frontend/src/pages/ProfilePage.jsx`
- `frontend/src/components/home/QuickStats.jsx`

---

### Stage 6: Image Upload & File Handling 🖼️
**Branch:** `feature/stage-6-image-upload`
**Priority:** MEDIUM
**Estimated Context:** 30-40%

#### Goals
- Connect frontend image upload UI to backend endpoint
- Handle file validation and progress tracking
- Display uploaded images in artwork cards/details
- Add placeholder images for artworks without images

#### Prerequisites
- Stage 4 complete (backend image upload endpoint implemented)
- Stage 3 complete (artwork pages integrated)

#### Tasks

**1. Create Image Upload Component**

**File:** `frontend/src/components/ImageUpload.jsx` (CREATE NEW)

```javascript
import { useState, useRef } from 'react';
import { Box, Button, Image, Text, Progress, useToast } from '@chakra-ui/react';
import { artworkService } from '../services/api';

export default function ImageUpload({ artworkId, currentImageUrl, onUploadSuccess }) {
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState(currentImageUrl);
  const fileInputRef = useRef(null);
  const toast = useToast();

  const handleFileSelect = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      toast({
        title: 'Invalid file type',
        description: 'Please upload a JPEG, PNG, or WebP image',
        status: 'error',
      });
      return;
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast({
        title: 'File too large',
        description: 'Maximum file size is 5MB',
        status: 'error',
      });
      return;
    }

    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => setPreview(e.target.result);
    reader.readAsDataURL(file);

    // Upload to backend
    setUploading(true);
    try {
      const result = await artworkService.uploadImage(artworkId, file);
      toast({
        title: 'Image uploaded successfully',
        status: 'success',
      });
      if (onUploadSuccess) onUploadSuccess(result.image_url);
    } catch (error) {
      toast({
        title: 'Upload failed',
        description: error.response?.data?.detail || error.message,
        status: 'error',
      });
    } finally {
      setUploading(false);
    }
  };

  return (
    <Box>
      <Box
        border="2px dashed"
        borderColor="gray.300"
        borderRadius="md"
        p={4}
        textAlign="center"
        cursor="pointer"
        onClick={() => fileInputRef.current.click()}
      >
        {preview ? (
          <Image src={preview} maxH="300px" mx="auto" />
        ) : (
          <Text color="gray.500">Click to upload image</Text>
        )}
      </Box>

      <input
        type="file"
        ref={fileInputRef}
        accept="image/jpeg,image/png,image/webp"
        style={{ display: 'none' }}
        onChange={handleFileSelect}
      />

      {uploading && <Progress isIndeterminate mt={2} />}

      <Button
        mt={2}
        size="sm"
        onClick={() => fileInputRef.current.click()}
        isLoading={uploading}
      >
        {preview ? 'Change Image' : 'Upload Image'}
      </Button>
    </Box>
  );
}
```

**2. Add Image Upload to AddArtworkPage**

**File:** `frontend/src/pages/AddArtworkPage.jsx` (MODIFY)

Add image upload after artwork creation:
```javascript
const createArtworkMutation = useMutation({
  mutationFn: (artworkData) => artworkService.create(artworkData),
  onSuccess: async (data) => {
    // If user selected image, upload it
    if (selectedImage) {
      try {
        await artworkService.uploadImage(data.id, selectedImage);
      } catch (error) {
        toast({
          title: 'Artwork created but image upload failed',
          description: error.message,
          status: 'warning',
        });
      }
    }

    toast({ title: 'Artwork created successfully', status: 'success' });
    navigate(`/artworks/${data.id}`);
  },
});
```

**3. Add Image Upload to Seller's Artwork Edit**

**File:** `frontend/src/pages/SellerDashboard.jsx` (MODIFY)

Add `ImageUpload` component to `SellerArtworkCard`:
```javascript
function SellerArtworkCard({ artwork }) {
  const queryClient = useQueryClient();

  const handleImageUpload = (newImageUrl) => {
    // Refresh artwork data
    queryClient.invalidateQueries(['my-artworks']);
  };

  return (
    <Box border="1px" borderColor="gray.200" p={4} borderRadius="md">
      <ImageUpload
        artworkId={artwork.id}
        currentImageUrl={artwork.image_url}
        onUploadSuccess={handleImageUpload}
      />

      {/* Rest of artwork details */}
      <Heading size="sm">{artwork.title}</Heading>
      <Text>Secret Threshold: ${artwork.secret_threshold}</Text>
      <Text>Current Bid: ${artwork.current_highest_bid}</Text>
    </Box>
  );
}
```

**4. Add Placeholder Images**

**File:** `frontend/src/components/ArtworkCard.jsx` (MODIFY)

Use placeholder when no image:
```javascript
function ArtworkCard({ artwork }) {
  const placeholderImage = 'https://via.placeholder.com/400x300?text=No+Image';

  return (
    <Box borderWidth="1px" borderRadius="lg" overflow="hidden">
      <Image
        src={artwork.image_url || placeholderImage}
        alt={artwork.title}
        objectFit="cover"
        h="200px"
        w="100%"
        fallbackSrc={placeholderImage}
      />

      {/* Rest of card content */}
    </Box>
  );
}
```

**5. Serve Static Files from Backend**

Verify `backend/main.py` has static file serving (added in Stage 4):
```python
from fastapi.staticfiles import StaticFiles

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
```

Create `uploads/artworks/` directory:
```bash
mkdir -p backend/uploads/artworks
```

Add to `.gitignore`:
```
backend/uploads/
```

#### Validation Steps
1. ✅ **Test image upload on new artwork**:
   - Create artwork with image
   - Verify image uploads successfully
   - Verify image displays in artwork detail
2. ✅ **Test image upload on existing artwork**:
   - Go to seller dashboard
   - Upload image to existing artwork
   - Verify image updates
3. ✅ **Test file validation**:
   - Try uploading non-image file → Error message
   - Try uploading file > 5MB → Error message
4. ✅ **Test placeholder images**:
   - Create artwork without image
   - Verify placeholder displays in cards/detail pages
5. ✅ **Test image serving**:
   - Upload image
   - Access directly via `/uploads/artworks/{filename}` → Should display

#### Files Modified
- `frontend/src/components/ImageUpload.jsx` (new)
- `frontend/src/pages/AddArtworkPage.jsx`
- `frontend/src/pages/SellerDashboard.jsx`
- `frontend/src/components/ArtworkCard.jsx`
- `backend/.gitignore`

---

### Stage 7: WebSocket Real-Time Features ⚡
**Branch:** `feature/stage-7-websocket-realtime`
**Priority:** MEDIUM
**Estimated Context:** 40-50%

#### Goals
- Emit socket events from backend when bids are placed
- Enable WebSocket client in frontend
- Connect frontend components to real-time bid updates
- Update UI in real-time when new bids arrive

#### Prerequisites
- Stage 1 complete (WebSocket authentication implemented)
- Stage 3 complete (bidding functionality working)

#### Tasks

**1. Emit Socket Events from Backend**

**File:** `backend/routers/bids.py` (MODIFY - uncomment lines 65-67)

```python
from main import sio  # Import socket.io server

@router.post("/", response_model=BidResponse)
async def create_bid(
    bid: BidCreate,
    current_user: User = Depends(require_buyer),
    db: Session = Depends(get_db)
):
    # ... existing bid creation logic ...

    db.add(db_bid)
    db.commit()
    db.refresh(db_bid)

    # ✅ EMIT SOCKET EVENT
    await sio.emit(
        "new_bid",
        {
            "bid": {
                "id": db_bid.id,
                "artwork_id": db_bid.artwork_id,
                "amount": float(db_bid.amount),
                "is_winning": db_bid.is_winning,
                "bid_time": db_bid.bid_time.isoformat(),
            },
            "artwork": {
                "id": artwork.id,
                "current_highest_bid": float(artwork.current_highest_bid),
                "status": artwork.status.value,
            }
        },
        room=f"artwork_{artwork.id}"
    )

    # If winning bid, emit artwork_sold event
    if db_bid.is_winning:
        await sio.emit(
            "artwork_sold",
            {
                "artwork_id": artwork.id,
                "winning_bid": float(db_bid.amount),
                "winner_id": current_user.id,
            },
            room=f"artwork_{artwork.id}"
        )

    return db_bid
```

**2. Enable WebSocket Client in Frontend**

**File:** `frontend/src/main.jsx` (MODIFY)

Enable socket service on app initialization:
```javascript
import { socketService } from './services/socket';

// Enable WebSocket connection
socketService.enable();

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

**3. Update Socket Service to Pass Token**

**File:** `frontend/src/services/socket.js` (MODIFY)

Pass JWT token in connection query params:
```javascript
class SocketService {
  enable() {
    if (this.enabled) return;
    this.enabled = true;

    // Get token from localStorage
    const token = localStorage.getItem('access_token');

    // Connect with token in query params
    this.socket = io(socketUrl, {
      query: { token },
      autoConnect: true,
    });

    this.setupEventListeners();
  }

  // ... rest of class ...
}
```

**4. Create Real-Time Bid Hook**

**File:** `frontend/src/hooks/useRealtimeBids.js` (CREATE NEW)

```javascript
import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { socketService } from '../services/socket';
import useBiddingStore from '../store/biddingStore';
import { useToast } from '@chakra-ui/react';

export function useRealtimeBids(artworkId) {
  const queryClient = useQueryClient();
  const { updateBid, markArtworkSold } = useBiddingStore();
  const toast = useToast();

  useEffect(() => {
    if (!artworkId) return;

    // Join artwork room
    socketService.joinArtwork(artworkId);

    // Listen for new bids
    const handleNewBid = (data) => {
      console.log('New bid received:', data);

      // Update bidding store
      updateBid(artworkId, data.bid);

      // Invalidate queries to refresh UI
      queryClient.invalidateQueries(['bids', artworkId]);
      queryClient.invalidateQueries(['artwork', artworkId]);

      // Show toast notification
      toast({
        title: 'New bid placed!',
        description: `$${data.bid.amount}`,
        status: 'info',
        duration: 3000,
        position: 'top-right',
      });
    };

    // Listen for artwork sold
    const handleArtworkSold = (data) => {
      console.log('Artwork sold:', data);

      // Update store
      markArtworkSold(artworkId);

      // Invalidate queries
      queryClient.invalidateQueries(['artwork', artworkId]);

      // Show success message
      toast({
        title: 'Auction Ended!',
        description: `Sold for $${data.winning_bid}`,
        status: 'success',
        duration: 5000,
        position: 'top',
      });
    };

    // Register event handlers
    socketService.onNewBid(handleNewBid);
    socketService.onArtworkSold(handleArtworkSold);

    // Cleanup on unmount
    return () => {
      socketService.leaveArtwork(artworkId);
      // Note: Don't remove listeners, they're global
    };
  }, [artworkId, queryClient, updateBid, markArtworkSold, toast]);
}
```

**5. Use Real-Time Hook in ArtworkPage**

**File:** `frontend/src/pages/ArtworkPage.jsx` (MODIFY)

```javascript
import { useRealtimeBids } from '../hooks/useRealtimeBids';

function ArtworkPage() {
  const { id } = useParams();

  // ... existing queries ...

  // Enable real-time updates
  useRealtimeBids(id);

  // ... rest of component ...
}
```

**6. Update BiddingStore to Handle Real-Time Updates**

**File:** `frontend/src/store/biddingStore.js` (VERIFY)

Ensure store methods work correctly (should already be implemented from previous analysis):
```javascript
const useBiddingStore = create((set) => ({
  activeArtworks: new Map(),
  currentBids: new Map(),
  socketConnected: false,

  updateBid: (artworkId, bidData) => set((state) => {
    const newBids = new Map(state.currentBids);
    newBids.set(artworkId, bidData);

    // Also update artwork's current_highest_bid
    const newArtworks = new Map(state.activeArtworks);
    const artwork = newArtworks.get(artworkId);
    if (artwork) {
      artwork.current_highest_bid = bidData.amount;
      newArtworks.set(artworkId, artwork);
    }

    return { currentBids: newBids, activeArtworks: newArtworks };
  }),

  markArtworkSold: (artworkId) => set((state) => {
    const newArtworks = new Map(state.activeArtworks);
    const artwork = newArtworks.get(artworkId);
    if (artwork) {
      artwork.status = 'SOLD';
      newArtworks.set(artworkId, artwork);
    }
    return { activeArtworks: newArtworks };
  }),

  // ... rest of store ...
}));
```

**7. Add Connection Status Indicator**

**File:** `frontend/src/components/SocketStatus.jsx` (CREATE NEW)

```javascript
import { useEffect, useState } from 'react';
import { Box, Text, Badge } from '@chakra-ui/react';
import { socketService } from '../services/socket';

export default function SocketStatus() {
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const checkConnection = () => {
      setConnected(socketService.socket?.connected || false);
    };

    // Check immediately
    checkConnection();

    // Check every 5 seconds
    const interval = setInterval(checkConnection, 5000);

    return () => clearInterval(interval);
  }, []);

  if (!connected) return null;

  return (
    <Box position="fixed" bottom={4} right={4} zIndex={1000}>
      <Badge colorScheme={connected ? 'green' : 'red'}>
        {connected ? '🟢 Live' : '🔴 Disconnected'}
      </Badge>
    </Box>
  );
}
```

Add to main layout or `App.jsx`:
```javascript
import SocketStatus from './components/SocketStatus';

function App() {
  return (
    <>
      <SocketStatus />
      {/* Rest of app */}
    </>
  );
}
```

#### Validation Steps
1. ✅ **Test WebSocket connection**:
   - Open browser console
   - Verify socket connection successful
   - Verify JWT token passed in query params
2. ✅ **Test real-time bid updates**:
   - Open artwork detail page in two browser windows
   - Place bid in one window
   - Verify other window updates immediately with new bid
   - Verify toast notification appears
3. ✅ **Test artwork sold event**:
   - Place winning bid (>= secret threshold)
   - Verify "Auction Ended" message appears
   - Verify artwork status changes to SOLD
4. ✅ **Test room management**:
   - Join artwork page → Verify joined room
   - Leave page → Verify left room
   - Navigate between artworks → Verify rooms switch correctly
5. ✅ **Test connection status**:
   - Verify green badge appears when connected
   - Stop backend → Verify badge turns red
   - Restart backend → Verify reconnection

#### Files Modified
- `backend/routers/bids.py`
- `frontend/src/main.jsx`
- `frontend/src/services/socket.js`
- `frontend/src/hooks/useRealtimeBids.js` (new)
- `frontend/src/pages/ArtworkPage.jsx`
- `frontend/src/store/biddingStore.js`
- `frontend/src/components/SocketStatus.jsx` (new)
- `frontend/src/App.jsx`

---

### Stage 8: Error Handling & Validation 🛡️
**Branch:** `feature/stage-8-error-handling`
**Priority:** MEDIUM
**Estimated Context:** 30-40%

#### Goals
- Add comprehensive input validation on backend
- Improve error messages for better user experience
- Add proper error handling in frontend
- Implement retry logic for failed requests

#### Prerequisites
- Stage 3 complete (frontend API integration)
- Stage 4 complete (backend endpoints)

#### Tasks

**1. Add Backend Input Validation**

**File:** `backend/routers/artworks.py` (MODIFY)

Add validation to artwork creation:
```python
@router.post("/", response_model=ArtworkResponse)
async def create_artwork(
    artwork: ArtworkCreate,
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db)
):
    # Validate secret_threshold
    if artwork.secret_threshold < 0:
        raise HTTPException(
            status_code=400,
            detail="Secret threshold must be non-negative"
        )

    # Validate title length
    if len(artwork.title) < 3 or len(artwork.title) > 200:
        raise HTTPException(
            status_code=400,
            detail="Title must be between 3 and 200 characters"
        )

    # Validate end_date is in future
    if artwork.end_date and artwork.end_date < datetime.utcnow():
        raise HTTPException(
            status_code=400,
            detail="End date must be in the future"
        )

    # ... rest of creation logic ...
```

**2. Add Pagination Limits**

**File:** `backend/routers/artworks.py` (MODIFY)

```python
@router.get("/", response_model=List[ArtworkResponse])
async def get_artworks(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    # Enforce max limit
    if limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit cannot exceed 100"
        )

    if skip < 0 or limit < 1:
        raise HTTPException(
            status_code=400,
            detail="Invalid pagination parameters"
        )

    artworks = db.query(Artwork).offset(skip).limit(limit).all()
    return artworks
```

**3. Add Custom Error Responses**

**File:** `backend/utils/errors.py` (CREATE NEW)

```python
from fastapi import HTTPException, status

class ArtworkNotFoundError(HTTPException):
    def __init__(self, artwork_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Artwork with id {artwork_id} not found"
        )

class UnauthorizedError(HTTPException):
    def __init__(self, message: str = "Not authorized"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )

class ValidationError(HTTPException):
    def __init__(self, field: str, message: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"field": field, "message": message}
        )
```

Use in routers:
```python
from utils.errors import ArtworkNotFoundError, UnauthorizedError

# Instead of:
if not artwork:
    raise HTTPException(status_code=404, detail="Artwork not found")

# Use:
if not artwork:
    raise ArtworkNotFoundError(artwork_id)
```

**4. Add Frontend Error Interceptor**

**File:** `frontend/src/services/api.js` (MODIFY)

Improve error handling:
```javascript
class API {
  async request(method, endpoint, options = {}) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method,
        headers: this.getHeaders(options.headers),
        body: options.body ? JSON.stringify(options.body) : undefined,
      });

      // Parse response
      const data = await response.json().catch(() => null);

      if (!response.ok) {
        // Create detailed error object
        const error = new Error(data?.detail || `HTTP ${response.status}`);
        error.status = response.status;
        error.data = data;

        // Handle specific status codes
        if (response.status === 401) {
          localStorage.removeItem('access_token');
          window.location.href = '/login';
        }

        if (response.status === 403) {
          error.message = 'You do not have permission to perform this action';
        }

        if (response.status === 404) {
          error.message = data?.detail || 'Resource not found';
        }

        if (response.status >= 500) {
          error.message = 'Server error. Please try again later.';
        }

        throw error;
      }

      return data;
    } catch (error) {
      if (error.status) throw error; // Already handled above

      // Network error
      console.error('Network error:', error);
      const networkError = new Error('Unable to connect to server');
      networkError.isNetworkError = true;
      throw networkError;
    }
  }
}
```

**5. Add React Query Error Handling**

**File:** `frontend/src/main.jsx` (MODIFY)

Configure global error handling:
```javascript
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useToast } from '@chakra-ui/react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: (failureCount, error) => {
        // Don't retry on 4xx errors (client errors)
        if (error.status >= 400 && error.status < 500) return false;
        // Retry up to 2 times for 5xx and network errors
        return failureCount < 2;
      },
      staleTime: 10000,
      onError: (error) => {
        console.error('Query error:', error);
      },
    },
    mutations: {
      retry: false, // Don't retry mutations
      onError: (error) => {
        console.error('Mutation error:', error);
      },
    },
  },
});
```

**6. Create Error Display Component**

**File:** `frontend/src/components/ErrorMessage.jsx` (CREATE NEW)

```javascript
import { Alert, AlertIcon, AlertTitle, AlertDescription, Button, Box } from '@chakra-ui/react';

export default function ErrorMessage({ error, onRetry }) {
  if (!error) return null;

  const getErrorMessage = () => {
    if (error.isNetworkError) {
      return 'Unable to connect to server. Please check your internet connection.';
    }

    if (error.status === 401) {
      return 'Your session has expired. Please log in again.';
    }

    if (error.status === 403) {
      return 'You do not have permission to access this resource.';
    }

    if (error.status === 404) {
      return 'The requested resource was not found.';
    }

    if (error.status >= 500) {
      return 'A server error occurred. Our team has been notified. Please try again later.';
    }

    return error.message || 'An unexpected error occurred.';
  };

  return (
    <Alert status="error" borderRadius="md">
      <AlertIcon />
      <Box flex="1">
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{getErrorMessage()}</AlertDescription>
      </Box>
      {onRetry && (
        <Button size="sm" onClick={onRetry} ml={4}>
          Retry
        </Button>
      )}
    </Alert>
  );
}
```

**7. Add Form Validation**

**File:** `frontend/src/components/ArtworkForm.jsx` (if exists, or create)

```javascript
import { useForm } from 'react-hook-form';

export default function ArtworkForm({ onSubmit, isLoading }) {
  const { register, handleSubmit, formState: { errors } } = useForm();

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <FormControl isInvalid={errors.title}>
        <FormLabel>Title</FormLabel>
        <Input
          {...register('title', {
            required: 'Title is required',
            minLength: { value: 3, message: 'Title must be at least 3 characters' },
            maxLength: { value: 200, message: 'Title cannot exceed 200 characters' },
          })}
        />
        <FormErrorMessage>{errors.title?.message}</FormErrorMessage>
      </FormControl>

      <FormControl isInvalid={errors.secret_threshold}>
        <FormLabel>Secret Threshold</FormLabel>
        <Input
          type="number"
          step="0.01"
          {...register('secret_threshold', {
            required: 'Secret threshold is required',
            min: { value: 0, message: 'Threshold must be non-negative' },
          })}
        />
        <FormErrorMessage>{errors.secret_threshold?.message}</FormErrorMessage>
      </FormControl>

      <FormControl isInvalid={errors.end_date}>
        <FormLabel>End Date</FormLabel>
        <Input
          type="datetime-local"
          {...register('end_date', {
            validate: (value) => {
              if (!value) return true;
              const date = new Date(value);
              return date > new Date() || 'End date must be in the future';
            },
          })}
        />
        <FormErrorMessage>{errors.end_date?.message}</FormErrorMessage>
      </FormControl>

      <Button type="submit" mt={4} isLoading={isLoading}>
        Create Artwork
      </Button>
    </form>
  );
}
```

#### Validation Steps
1. ✅ **Test backend validation**:
   - Try creating artwork with negative threshold → 400 error
   - Try creating artwork with title < 3 chars → 400 error
   - Try creating artwork with end_date in past → 400 error
2. ✅ **Test pagination limits**:
   - Request `?limit=1000` → 400 error
   - Request `?limit=-1` → 400 error
3. ✅ **Test frontend error handling**:
   - Trigger 404 error → Shows "not found" message
   - Trigger 401 error → Redirects to login
   - Trigger network error → Shows connection error
4. ✅ **Test retry logic**:
   - Trigger network error → Retries up to 2 times
   - Trigger 400 error → Does not retry
5. ✅ **Test form validation**:
   - Submit form with invalid data → Shows error messages
   - Submit form with valid data → Submits successfully

#### Files Modified
- `backend/routers/artworks.py`
- `backend/routers/bids.py`
- `backend/utils/errors.py` (new)
- `frontend/src/services/api.js`
- `frontend/src/main.jsx`
- `frontend/src/components/ErrorMessage.jsx` (new)
- `frontend/src/components/ArtworkForm.jsx` (new or modified)

---

### Stage 9: Performance Optimization 🚀
**Branch:** `feature/stage-9-performance`
**Priority:** MEDIUM
**Estimated Context:** 30-40%

#### Goals
- Fix N+1 query problems with eager loading
- Add database query optimization
- Implement frontend code splitting
- Optimize image loading

#### Prerequisites
- All previous stages complete
- Application functionally working

#### Tasks

**1. Fix N+1 Queries with Eager Loading**

**File:** `backend/routers/bids.py` (MODIFY)

```python
from sqlalchemy.orm import joinedload

@router.get("/artwork/{artwork_id}", response_model=List[BidResponse])
async def get_bids_by_artwork(
    artwork_id: int,
    db: Session = Depends(get_db)
):
    # Use eager loading to prevent N+1 queries
    bids = db.query(Bid).options(
        joinedload(Bid.artwork),
        joinedload(Bid.bidder)
    ).filter(Bid.artwork_id == artwork_id).all()

    return bids
```

**File:** `backend/routers/artworks.py` (MODIFY)

```python
@router.get("/", response_model=List[ArtworkResponse])
async def get_artworks(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    # Eager load seller relationship
    artworks = db.query(Artwork).options(
        joinedload(Artwork.seller)
    ).offset(skip).limit(limit).all()

    return artworks

@router.get("/my-artworks", response_model=List[ArtworkWithSecretResponse])
async def get_my_artworks(
    current_user: User = Depends(require_seller),
    db: Session = Depends(get_db)
):
    # Eager load bids for each artwork
    artworks = db.query(Artwork).options(
        joinedload(Artwork.bids)
    ).filter(Artwork.seller_id == current_user.id).all()

    return artworks
```

**2. Add Database Query Logging**

**File:** `backend/database.py` (MODIFY)

Enable query logging in development:
```python
import os

# Enable SQL echo in development
echo = os.getenv("ENVIRONMENT", "development") == "development"

engine = create_engine(
    DATABASE_URL,
    echo=echo,  # ✅ Enable query logging
    # ... rest of config
)
```

**3. Add React Code Splitting**

**File:** `frontend/src/App.jsx` (MODIFY)

```javascript
import { lazy, Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Spinner, Center } from '@chakra-ui/react';

// Eager load critical pages
import HomePage from './pages/HomePage';
import ArtworksPage from './pages/ArtworksPage';

// Lazy load other pages
const ArtworkPage = lazy(() => import('./pages/ArtworkPage'));
const UserDashboard = lazy(() => import('./pages/UserDashboard'));
const SellerDashboard = lazy(() => import('./pages/SellerDashboard'));
const AdminDashboard = lazy(() => import('./pages/AdminDashboard'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const AddArtworkPage = lazy(() => import('./pages/AddArtworkPage'));

function App() {
  return (
    <Suspense fallback={
      <Center h="100vh">
        <Spinner size="xl" />
      </Center>
    }>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/artworks" element={<ArtworksPage />} />
        <Route path="/artworks/:id" element={<ArtworkPage />} />
        <Route path="/dashboard" element={<UserDashboard />} />
        <Route path="/seller" element={<SellerDashboard />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/sell" element={<AddArtworkPage />} />
      </Routes>
    </Suspense>
  );
}
```

**4. Optimize Image Loading**

**File:** `frontend/src/components/ArtworkCard.jsx` (MODIFY)

```javascript
import { useState } from 'react';

function ArtworkCard({ artwork }) {
  const [imageLoaded, setImageLoaded] = useState(false);

  return (
    <Box>
      <Box position="relative" bg="gray.100">
        {!imageLoaded && (
          <Skeleton h="200px" w="100%" />
        )}
        <Image
          src={artwork.image_url}
          alt={artwork.title}
          loading="lazy" // ✅ Native lazy loading
          onLoad={() => setImageLoaded(true)}
          display={imageLoaded ? 'block' : 'none'}
        />
      </Box>
      {/* Rest of card */}
    </Box>
  );
}
```

**5. Add React Query Cache Configuration**

**File:** `frontend/src/main.jsx` (MODIFY)

```javascript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60000, // 1 minute
      cacheTime: 300000, // 5 minutes
      refetchOnWindowFocus: false, // Don't refetch on window focus
      refetchOnMount: false, // Don't refetch on component mount if data exists
    },
  },
});
```

**6. Optimize Backend Response Size**

**File:** `backend/schemas/artwork.py` (MODIFY)

Remove unnecessary fields from responses:
```python
class ArtworkResponse(ArtworkBase):
    id: int
    seller_id: int
    current_highest_bid: float
    status: ArtworkStatus
    created_at: datetime

    # Only include image_url if it exists (omit null)
    image_url: Optional[str] = None

    class Config:
        orm_mode = True
        # Exclude None values from response
        json_encoders = {
            type(None): lambda v: None
        }
```

#### Validation Steps
1. ✅ **Test N+1 query fixes**:
   - Enable SQL logging
   - Load artworks page
   - Verify only 1-2 queries instead of N+1
2. ✅ **Test code splitting**:
   - Run `npm run build`
   - Check bundle sizes in `dist/`
   - Verify multiple JS chunks created
3. ✅ **Test lazy loading**:
   - Open Network tab
   - Navigate to different pages
   - Verify page-specific JS loads on demand
4. ✅ **Test image lazy loading**:
   - Scroll artworks page
   - Verify images load as they enter viewport

#### Files Modified
- `backend/routers/bids.py`
- `backend/routers/artworks.py`
- `backend/database.py`
- `backend/schemas/artwork.py`
- `frontend/src/App.jsx`
- `frontend/src/components/ArtworkCard.jsx`
- `frontend/src/main.jsx`

---

### Stage 10: Comprehensive Testing Suite 🧪
**Branch:** `feature/stage-10-testing`
**Priority:** HIGH
**Estimated Context:** 40-50%

#### Goals
- Expand backend test coverage
- Test all critical security fixes
- Test real-time WebSocket functionality
- Run full test suite and verify coverage

#### Prerequisites
- ALL previous stages complete
- Application fully functional

#### Tasks

**1. Test Authentication & Authorization**

**File:** `backend/tests/integration/test_auth_fixes.py` (CREATE NEW)

```python
import pytest
from fastapi.testclient import TestClient

def test_create_artwork_requires_auth(client):
    """Test that creating artwork requires authentication."""
    response = client.post("/api/artworks/", json={
        "title": "Test Art",
        "secret_threshold": 100.0
    })
    assert response.status_code == 401

def test_seller_id_extracted_from_token(client, seller_token, db_session):
    """Test that seller_id comes from token, not query param."""
    response = client.post(
        "/api/artworks/",
        json={"title": "Test Art", "secret_threshold": 100.0},
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    assert response.status_code == 200
    # Verify seller_id matches token owner
    data = response.json()
    # TODO: Add assertion to verify seller_id matches authenticated user

def test_cannot_bid_on_own_artwork(client, seller_token, seller_user, db_session):
    """Test seller cannot bid on their own artwork."""
    # Create artwork as seller
    artwork_response = client.post(
        "/api/artworks/",
        json={"title": "My Art", "secret_threshold": 100.0},
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    artwork_id = artwork_response.json()["id"]

    # Try to bid on own artwork
    bid_response = client.post(
        "/api/bids/",
        json={"artwork_id": artwork_id, "amount": 150.0},
        headers={"Authorization": f"Bearer {seller_token}"}
    )
    assert bid_response.status_code == 400
    assert "cannot bid on your own artwork" in bid_response.json()["detail"].lower()

def test_websocket_requires_token():
    """Test WebSocket connection requires token."""
    # TODO: Test WebSocket connection without token → rejected
    # TODO: Test WebSocket connection with valid token → accepted
    pass
```

**2. Test Database Migrations**

**File:** `backend/tests/integration/test_migrations.py` (CREATE NEW)

```python
def test_artwork_has_new_fields(db_session):
    """Test that artwork model has new fields from migration."""
    from models.artwork import Artwork

    # Create artwork with new fields
    artwork = Artwork(
        seller_id=1,
        title="Test",
        secret_threshold=100,
        artist_name="Test Artist",  # New field
        category="Painting",  # New field
        end_date=datetime.now() + timedelta(days=7)  # New field
    )
    db_session.add(artwork)
    db_session.commit()

    # Verify fields saved
    assert artwork.artist_name == "Test Artist"
    assert artwork.category == "Painting"
    assert artwork.end_date is not None

def test_indexes_exist(db_session):
    """Test that indexes were created."""
    # Query database metadata to verify indexes
    from sqlalchemy import inspect
    inspector = inspect(db_session.bind)

    # Check artwork indexes
    artwork_indexes = inspector.get_indexes('artworks')
    index_names = [idx['name'] for idx in artwork_indexes]

    assert 'idx_artwork_seller_id' in index_names
    assert 'idx_artwork_status' in index_names

    # Check bid indexes
    bid_indexes = inspector.get_indexes('bids')
    bid_index_names = [idx['name'] for idx in bid_indexes]

    assert 'idx_bid_artwork_id' in bid_index_names
    assert 'idx_bid_bidder_id' in bid_index_names
```

**3. Test WebSocket Events**

**File:** `backend/tests/integration/test_websocket.py` (CREATE NEW)

```python
import pytest
from socketio import AsyncClient

@pytest.mark.asyncio
async def test_bid_emits_socket_event(client, buyer_token, artwork, db_session):
    """Test that placing bid emits socket event."""
    # TODO: Connect socket.io client
    # TODO: Join artwork room
    # TODO: Place bid via REST API
    # TODO: Verify socket event received
    pass

@pytest.mark.asyncio
async def test_winning_bid_emits_sold_event(client, buyer_token, artwork, db_session):
    """Test that winning bid emits artwork_sold event."""
    # TODO: Similar to above but with winning bid
    pass
```

**4. Test Image Upload**

**File:** `backend/tests/integration/test_image_upload.py` (CREATE NEW)

```python
from io import BytesIO
from PIL import Image

def test_upload_valid_image(client, seller_token, artwork, db_session):
    """Test uploading valid image."""
    # Create test image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    response = client.post(
        f"/api/artworks/{artwork.id}/upload-image",
        files={"file": ("test.jpg", img_bytes, "image/jpeg")},
        headers={"Authorization": f"Bearer {seller_token}"}
    )

    assert response.status_code == 200
    assert "image_url" in response.json()

def test_upload_invalid_file_type(client, seller_token, artwork):
    """Test that invalid file types are rejected."""
    response = client.post(
        f"/api/artworks/{artwork.id}/upload-image",
        files={"file": ("test.txt", b"fake image", "text/plain")},
        headers={"Authorization": f"Bearer {seller_token}"}
    )

    assert response.status_code == 400

def test_upload_file_too_large(client, seller_token, artwork):
    """Test that files >5MB are rejected."""
    # Create 6MB file
    large_file = BytesIO(b"0" * (6 * 1024 * 1024))

    response = client.post(
        f"/api/artworks/{artwork.id}/upload-image",
        files={"file": ("large.jpg", large_file, "image/jpeg")},
        headers={"Authorization": f"Bearer {seller_token}"}
    )

    assert response.status_code == 400
```

**5. Test Stats Endpoints**

**File:** `backend/tests/integration/test_stats.py` (CREATE NEW)

```python
def test_user_stats(client, buyer_token, buyer_user, artwork, db_session):
    """Test user stats endpoint."""
    # Place some bids
    # TODO: Create bids for buyer_user

    response = client.get(
        "/api/stats/user",
        headers={"Authorization": f"Bearer {buyer_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "active_bids" in data
    assert "won_auctions" in data
    assert "total_spent" in data

def test_seller_stats(client, seller_token, seller_user, db_session):
    """Test seller stats endpoint."""
    response = client.get(
        "/api/stats/seller",
        headers={"Authorization": f"Bearer {seller_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "total_artworks" in data
    assert "active_auctions" in data
    assert "total_earnings" in data

def test_platform_stats(client):
    """Test public platform stats."""
    response = client.get("/api/stats/platform")

    assert response.status_code == 200
    data = response.json()
    assert "total_artworks" in data
    assert "total_users" in data
```

**6. Run Full Test Suite**

```bash
cd backend

# Run all tests with coverage
pytest --cov=. --cov-report=term-missing --cov-report=html

# Run specific test categories
pytest tests/unit/ -v
pytest tests/integration/ -v

# Check coverage report
open htmlcov/index.html
```

**Target Coverage:**
- Overall: >80%
- Critical paths (auth, bidding): >90%
- API endpoints: >85%

**7. Frontend Testing** (Optional - expand if time permits)

**File:** `frontend/src/test/integration/artworks.test.js`

```javascript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClientProvider } from '@tanstack/react-query';
import ArtworksPage from '../pages/ArtworksPage';

test('loads and displays artworks', async () => {
  render(
    <QueryClientProvider client={queryClient}>
      <ArtworksPage />
    </QueryClientProvider>
  );

  await waitFor(() => {
    expect(screen.getByText(/artworks/i)).toBeInTheDocument();
  });
});

// Add more integration tests as needed
```

#### Validation Steps
1. ✅ **Run backend tests**: `pytest --cov`
   - Verify >80% overall coverage
   - All tests pass
2. ✅ **Run frontend tests**: `npm test`
   - All tests pass
3. ✅ **Manual E2E testing**:
   - Complete user flow: Register → Browse → Bid → Win
   - Complete seller flow: Create artwork → Receive bids → Sell
   - Complete admin flow: View stats → Moderate content
4. ✅ **Security testing**:
   - Try forging seller_id → Rejected
   - Try accessing protected endpoints without auth → 401
   - Try bidding on own artwork → 400

#### Files Modified
- `backend/tests/integration/test_auth_fixes.py` (new)
- `backend/tests/integration/test_migrations.py` (new)
- `backend/tests/integration/test_websocket.py` (new)
- `backend/tests/integration/test_image_upload.py` (new)
- `backend/tests/integration/test_stats.py` (new)
- `frontend/src/test/integration/artworks.test.js` (new, optional)

---

## Post-Implementation Verification

After completing ALL stages, perform final verification:

### 1. Functionality Checklist

- [ ] **Authentication**
  - [ ] Users can register via Auth0
  - [ ] Users can log in and stay logged in on refresh
  - [ ] Protected routes redirect to login
  - [ ] Role-based access control works (buyer, seller, admin)

- [ ] **Artworks**
  - [ ] Can browse artworks with filters
  - [ ] Can view artwork details
  - [ ] Sellers can create artworks with images
  - [ ] Sellers can see their own artworks with secret thresholds
  - [ ] Can upload/change artwork images

- [ ] **Bidding**
  - [ ] Can place bids on active artworks
  - [ ] Bid validation works (negative amounts rejected)
  - [ ] Winning bids mark artwork as SOLD
  - [ ] Sellers cannot bid on own artworks
  - [ ] Real-time bid updates work via WebSocket

- [ ] **Dashboards**
  - [ ] User dashboard shows personal stats and bids
  - [ ] Seller dashboard shows inventory and sales
  - [ ] Profile page allows editing user info
  - [ ] Stats update in real-time

- [ ] **Performance**
  - [ ] Pages load quickly (<2s)
  - [ ] Images lazy load
  - [ ] No N+1 query issues

### 2. Security Checklist

- [ ] No hardcoded secrets in codebase
- [ ] All environment variables in `.env` files
- [ ] `.env` files in `.gitignore`
- [ ] Auth0 credentials secure
- [ ] User IDs extracted from tokens, not query params
- [ ] WebSocket connections authenticated
- [ ] CORS configured properly
- [ ] Input validation on all endpoints
- [ ] SQL injection prevented (using ORM)

### 3. Database Checklist

- [ ] All migrations applied successfully
- [ ] Indexes created on foreign keys
- [ ] New fields (artist_name, category, end_date) present
- [ ] Cascade deletions work correctly
- [ ] No orphaned records

### 4. Code Quality Checklist

- [ ] No ESLint errors in frontend
- [ ] No linting errors in backend
- [ ] Test coverage >80%
- [ ] All console.log removed from production code
- [ ] Error handling comprehensive
- [ ] Loading states on all async operations

### 5. Deployment Readiness

- [ ] Docker Compose works
- [ ] Backend health endpoints accessible
- [ ] Frontend builds successfully (`npm run build`)
- [ ] Environment variables documented in `.env.example`
- [ ] README updated with new setup instructions
- [ ] CI/CD pipeline runs successfully (if enabled)

---

## 🚨 Important Notes for Claude Code

### Before Starting Any Stage:

1. **Always create feature branch first** using GitFlow naming
2. **Read the entire stage** before starting implementation
3. **Check prerequisites** - don't skip stages
4. **Commit frequently** with descriptive messages

### During Implementation:

1. **Test as you go** - don't wait until the end to test
2. **Ask user for clarification** if requirements are unclear
3. **Report blockers immediately** - don't waste context on stuck issues
4. **Watch context usage** - if approaching limit, summarize progress and stop

### After Completing Stage:

1. **Run validation steps** listed in the stage
2. **Commit all changes** with meaningful commit message
3. **Merge to dev branch** using `--no-ff`
4. **Report completion** to user with summary of changes
5. **Ask permission** before starting next stage

### Special Warnings:

- ⚠️ **NEVER modify CI/CD pipeline** without explicit user permission
- ⚠️ **NEVER commit `.env` files** to git
- ⚠️ **NEVER skip authentication** on protected endpoints
- ⚠️ **NEVER merge directly to `main`** - always use `dev` first
- ⚠️ **ALWAYS verify secrets are in environment variables** before committing

### If You Get Stuck:

1. Document what you tried
2. Document the error/blocker
3. Ask user for guidance
4. Don't waste context repeatedly trying the same approach

---

## Appendix: Quick Reference

### Useful Commands

**Backend:**
```bash
# Start backend
cd backend && uvicorn main:socket_app --reload

# Run migrations
alembic upgrade head

# Run tests
pytest --cov

# Create migration
alembic revision --autogenerate -m "description"
```

**Frontend:**
```bash
# Start frontend
cd frontend && npm run dev

# Build for production
npm run build

# Run tests
npm test

# Run linter
npm run lint
```

**Git:**
```bash
# Create feature branch
git checkout -b feature/stage-X-name

# Commit changes
git add .
git commit -m "feat: descriptive message"

# Merge to dev
git checkout dev
git merge feature/stage-X-name --no-ff
git push origin dev
```

### File Paths Quick Reference

**Backend:**
- Config: `backend/config/settings.py`
- Models: `backend/models/`
- Schemas: `backend/schemas/`
- Routers: `backend/routers/`
- Services: `backend/services/`
- Utils: `backend/utils/`
- Tests: `backend/tests/`

**Frontend:**
- Pages: `frontend/src/pages/`
- Components: `frontend/src/components/`
- Services: `frontend/src/services/`
- Store: `frontend/src/store/`
- Hooks: `frontend/src/hooks/`

---

**Document End** - Ready for implementation! 🚀
