
# Auth0 as Primary User Store - Migration Guide

## Overview
This guide outlines the steps to refactor the application to use Auth0 as the primary user store, moving user roles and profile data from the PostgreSQL database to Auth0, while keeping only minimal user references in the database.

## Current State

**Database (PostgreSQL):**
- `users` table stores: `id`, `auth0_sub`, `email`, `name`, `role`, `password_hash`, `created_at`
- `role` is stored as enum: `ADMIN`, `SELLER`, `BUYER`
- User authentication uses both Auth0 OAuth2 and email/password

**Auth0:**
- Handles OAuth2 authentication
- Stores user identity
- Not currently used for roles or user metadata

**Problems:**
- Duplicate user data between Auth0 and database
- Need to manually sync Auth0 users with database users
- Complex authentication logic (Auth0 + email/password)
- Hardcoded admin credentials for bootstrapping

## Target State

**Database (PostgreSQL):**
- `users` table stores ONLY: `id`, `auth0_sub`, `created_at`
- No role, email, name, or password_hash columns
- Users table is a lightweight reference for foreign keys

**Auth0:**
- Stores ALL user data: email, name, profile info
- Stores roles using Auth0 Authorization (Roles & Permissions)
- Single source of truth for user identity
- No hardcoded credentials needed

**Benefits:**
- Single source of truth for user data
- Leverage Auth0's built-in features (password reset, MFA, etc.)
- Simplified database schema
- No user data synchronization needed
- Roles managed through Auth0 Dashboard

---

## Prerequisites

Before starting this migration, ensure:

1. **Auth0 Dashboard Access**: You have admin access to the Auth0 tenant
2. **Auth0 API Configuration**: Auth0 API is configured with audience
3. **Database Backup**: Take a backup of production database
4. **Testing Environment**: Have a development/staging environment to test

## ⚠️ CRITICAL: Data Migration Strategy

**IMPORTANT**: This migration requires clearing all existing data from the production database due to incompatible user ID references.

### Why Database Clearing is Required

The existing database has foreign key relationships (artworks, bids, etc.) that reference user IDs. After the migration:
- User IDs will change (new users created with Auth0 references)
- Old user data (email, name, role, password) will be removed
- Foreign key relationships will be broken

### Options

**Option 1: Fresh Start (Recommended for Demo/Development)**
- Clear all data from production database
- Start with clean slate
- All users create new Auth0 accounts
- No data migration needed

**Option 2: Data Migration (Complex - Not covered in this guide)**
- Export existing data
- Create Auth0 users matching existing users
- Migrate data with new user ID mappings
- Requires custom migration scripts

**This guide assumes Option 1 (Fresh Start).**

### Database Clearing Step (Before Stage 9 Deployment)

Before deploying the migration, you must clear the production database:

```bash
# Connect to production database and run:
TRUNCATE TABLE bids CASCADE;
TRUNCATE TABLE artworks CASCADE;
TRUNCATE TABLE users CASCADE;
```

**OR** use the admin API endpoint (if available):
```bash
# Clear all data via API
curl -X POST "https://your-backend.azurewebsites.net/api/admin/clear-database" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

This step is documented in **Stage 9** but mentioned here for awareness.

---

## Stage 1: Configure Auth0 Roles

### Objective
Set up roles in Auth0 Dashboard so they can be included in JWT tokens.

### Steps

#### 1.1 Create Roles in Auth0 Dashboard

1. Log into Auth0 Dashboard (https://manage.auth0.com)
2. Navigate to **User Management** → **Roles**
3. Create three roles:
   - **Name**: `ADMIN`, **Description**: `Platform administrator with full access`
   - **Name**: `SELLER`, **Description**: `Can create and manage artworks`
   - **Name**: `BUYER`, **Description**: `Can place bids on artworks`

#### 1.2 Create Auth0 Action to Add Roles to Token

1. Navigate to **Actions** → **Library**
2. Click **"+ Build Custom"**
3. Create action with:
   - **Name**: `Add User Roles to Token`
   - **Trigger**: `Login / Post Login`
   - **Runtime**: Select the latest Node.js version (e.g., Node 22)
     - **Note**: This runtime is for Auth0's servers only and does not affect your application's Node version
   - **Code**:

```javascript
exports.onExecutePostLogin = async (event, api) => {
  const namespace = 'https://guesstheworth.demo';

  if (event.authorization) {
    // Add roles to access token
    api.accessToken.setCustomClaim(`${namespace}/roles`, event.authorization.roles);

    // Optionally add roles to ID token as well
    api.idToken.setCustomClaim(`${namespace}/roles`, event.authorization.roles);
  }
};
```

4. Click **"Deploy"**

#### 1.3 Add Action to Post-Login Trigger

1. Navigate to **Actions** → **Triggers** → **Post-Login**
2. Drag the "Add User Roles to Token" action from the right panel into the flow (between Start and Complete)
3. Click **"Apply"**

#### 1.4 Assign Roles to Existing Users (if any)

1. Navigate to **User Management** → **Users**
2. For each user, click their name → **Roles** tab
3. Assign appropriate role (ADMIN, SELLER, or BUYER)

---

## Stage 2: Update Backend Models

### Objective
Simplify the User model to store only minimal data, removing fields now managed by Auth0.

### Files to Modify

#### 2.1 Update `backend/models/user.py`

**Current state**: User model has `email`, `name`, `role`, `password_hash` columns

**Changes needed**:
1. Remove `UserRole` enum (roles come from Auth0)
2. Remove columns: `email`, `name`, `role`, `password_hash`
3. Keep only: `id`, `auth0_sub`, `created_at`
4. Update `__repr__` to show only `id` and `auth0_sub`

**Updated model should look like**:
```python
from datetime import UTC, datetime
from sqlalchemy import Column, DateTime, Integer, String
from database import Base

class User(Base):
    """User model - minimal reference to Auth0 user."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    auth0_sub = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    def __repr__(self):
        return f"<User(id={self.id}, auth0_sub='{self.auth0_sub}')>"
```

**Note**: Remove the entire `UserRole` enum class.

---

## Stage 3: Update Authentication Logic

### Objective
Update authentication to read user data (email, name, role) from Auth0 JWT tokens instead of database.

### Files to Modify

#### 3.1 Update `backend/utils/auth.py`

**Current state**:
- `get_current_user()` reads user from database
- Has hardcoded admin credentials
- Has password hashing functions

**Changes needed**:

1. **Remove password functions**: Delete `hash_password()` and `verify_password()`
2. **Remove hardcoded admin logic**: Delete temporary admin handling
3. **Update `get_current_user()` to extract data from token**:

```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from Auth0 token."""
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Try Auth0 token verification first
        userinfo = await verify_auth0_token(token)

        if userinfo:
            auth0_sub = userinfo.get("sub")

            # Get or create minimal user record in database
            user = db.query(User).filter(User.auth0_sub == auth0_sub).first()

            if not user:
                # Auto-create user reference on first login
                user = User(auth0_sub=auth0_sub)
                db.add(user)
                db.commit()
                db.refresh(user)

            # Attach Auth0 data to user object (not stored in DB)
            user.email = userinfo.get("email", "")
            user.name = userinfo.get("name", "")

            # Extract role from custom claim
            roles = userinfo.get("https://guesstheworth.demo/roles", [])
            user.role = roles[0] if roles else "BUYER"  # Default to BUYER

            return user

        # Try JWT token verification (for API-only access)
        payload = JWTService.verify_token(token)
        if payload:
            user_sub = payload.get("sub")

            # Get user from database
            user = None
            try:
                user_id = int(user_sub)
                user = db.query(User).filter(User.id == user_id).first()
            except (ValueError, TypeError):
                user = db.query(User).filter(User.auth0_sub == user_sub).first()

            if user:
                # Attach data from JWT payload
                user.email = payload.get("email", "")
                user.name = payload.get("name", "")
                user.role = payload.get("role", "BUYER")
                return user

        raise credentials_exception

    except Exception as e:
        print(f"Authentication error: {e}")
        raise credentials_exception
```

4. **Add helper function for role checking**:

```python
def require_role(required_role: str):
    """Dependency to require a specific role."""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if not hasattr(current_user, 'role') or current_user.role != required_role:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. {required_role} role required."
            )
        return current_user
    return role_checker
```

#### 3.2 Update `backend/routers/admin.py`

**Changes needed**:

1. Update `require_admin()` dependency:

```python
def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user is an admin."""
    if not hasattr(current_user, 'role') or current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
```

2. **Remove all bootstrap token logic**:
   - Remove `BOOTSTRAP_TOKEN` constants
   - Remove `bootstrap_token` parameters from endpoints
   - Simplify authentication to only use `require_admin`

3. **Remove `/stamp-migrations` endpoint** (was for bootstrapping)

4. **Update `/run-migrations` endpoint**:

```python
@router.post("/run-migrations")
async def run_migrations(
    current_user: User = Depends(require_admin),
):
    """Run database migrations (alembic upgrade head)."""
    try:
        import subprocess

        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd="/app",
        )

        if result.returncode != 0:
            raise Exception(f"Migration failed: {result.stderr}")

        return {
            "success": True,
            "message": "Migrations completed successfully",
            "output": result.stdout,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Migration failed: {str(e)}")
```

5. **Update `/seed-database` endpoint** (remove bootstrap logic):

```python
@router.post("/seed-database")
async def seed_database(
    confirm: str = Query(..., description="Must be 'yes' to confirm"),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """Seed the production database with demo data."""
    if confirm.lower() != "yes":
        raise HTTPException(
            status_code=400,
            detail="Must confirm with 'yes' query parameter to proceed with seeding",
        )
    # ... rest of seeding logic
```

#### 3.3 Remove `backend/routers/auth.py`

**Action**: Delete the entire `/api/auth/login` endpoint

**Reason**: No longer using email/password authentication, Auth0 handles all authentication

---

## Stage 4: Create Database Migration

### Objective
Create Alembic migration to remove unnecessary columns from users table.

### Steps

#### 4.1 Create New Migration

Run from backend directory:
```bash
alembic revision -m "remove_user_fields_use_auth0"
```

#### 4.2 Write Migration Code

In the generated migration file (e.g., `backend/alembic/versions/xxxxx_remove_user_fields_use_auth0.py`):

```python
"""Remove user fields - use Auth0

Revision ID: [auto-generated]
Revises: c3e5f7a8b2d1
Create Date: [auto-generated]
"""
from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '[auto-generated]'
down_revision: Union[str, None] = 'c3e5f7a8b2d1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove columns that are now managed by Auth0
    op.drop_column('users', 'password_hash')
    op.drop_column('users', 'email')
    op.drop_column('users', 'name')

    # Drop the role enum type and column
    op.drop_column('users', 'role')
    op.execute("DROP TYPE IF EXISTS userrole")


def downgrade() -> None:
    # Recreate userrole enum
    op.execute("CREATE TYPE userrole AS ENUM ('ADMIN', 'SELLER', 'BUYER')")

    # Add columns back
    op.add_column('users', sa.Column('role', sa.Enum('ADMIN', 'SELLER', 'BUYER', name='userrole'), nullable=False, server_default='BUYER'))
    op.add_column('users', sa.Column('name', sa.String(), nullable=False, server_default='Unknown'))
    op.add_column('users', sa.Column('email', sa.String(), nullable=False, server_default='unknown@example.com'))
    op.add_column('users', sa.Column('password_hash', sa.String(), nullable=True))
```

---

## Stage 5: Update Seed Scripts

### Objective
Update demo data seeding to work with new Auth0-centric model.

### Files to Modify

#### 5.1 Update `backend/seeds/demo_users.py`

**Current state**: Creates users with email, name, role, password

**Changes needed**:

```python
"""Seed demo users for testing and demonstration.

Creates minimal user records. User data (email, name, role) is managed in Auth0.
"""

from sqlalchemy.orm import Session
from models.user import User


def seed_users(db: Session) -> int:
    """Seed demo users with Auth0 references.

    IMPORTANT: Before running this, you must:
    1. Create corresponding users in Auth0 Dashboard
    2. Assign them roles (ADMIN, SELLER, BUYER)
    3. Use the auth0_sub values from Auth0 here

    This function is idempotent - safe to run multiple times.

    Args:
        db: Database session

    Returns:
        Number of users created or verified
    """
    # These auth0_sub values must match users created in Auth0
    demo_users = [
        {"auth0_sub": "auth0|demo-admin-001"},
        {"auth0_sub": "auth0|demo-seller-001"},
        {"auth0_sub": "auth0|demo-seller-002"},
        {"auth0_sub": "auth0|demo-seller-003"},
        {"auth0_sub": "auth0|demo-buyer-001"},
        {"auth0_sub": "auth0|demo-buyer-002"},
        {"auth0_sub": "auth0|demo-buyer-003"},
        {"auth0_sub": "auth0|demo-buyer-004"},
        {"auth0_sub": "auth0|demo-buyer-005"},
    ]

    created_count = 0

    for user_data in demo_users:
        # Check if user already exists (idempotency)
        existing_user = db.query(User).filter(
            User.auth0_sub == user_data["auth0_sub"]
        ).first()

        if not existing_user:
            # Create new user reference
            new_user = User(**user_data)
            db.add(new_user)
            print(f"   ✓ Created user reference: {user_data['auth0_sub']}")
        else:
            print(f"   ↻ User reference already exists: {user_data['auth0_sub']}")

        created_count += 1

    db.commit()
    return created_count


if __name__ == "__main__":
    """Allow running this seed script directly for testing."""
    import sys
    from pathlib import Path

    # Add backend directory to path
    backend_dir = Path(__file__).parent.parent
    sys.path.insert(0, str(backend_dir))

    from database import SessionLocal

    db = SessionLocal()
    try:
        count = seed_users(db)
        print(f"\n✅ Seeded {count} user references successfully!")
        print("\n⚠️  IMPORTANT: Make sure these users exist in Auth0 with matching auth0_sub values!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
```

#### 5.2 Update Documentation

**File**: `backend/seeds/AZURE_SEEDING.md`

Update the seeding instructions to mention:
1. Users must be created in Auth0 first
2. Roles must be assigned in Auth0
3. The seeding script only creates database references

---

## Stage 6: Update Admin Endpoints

### Objective
Update admin endpoints to work with Auth0 user data.

### Files to Modify

#### 6.1 Update `backend/routers/admin.py`

**List users endpoint** (`GET /api/admin/users`):

```python
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
    List all users.

    NOTE: This returns minimal user data from database.
    For full user details (email, name, role), query Auth0 Management API.
    """
    query = db.query(User)

    # Get total count
    total = query.count()

    # Get paginated results
    users = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "users": [
            {
                "id": user.id,
                "auth0_sub": user.auth0_sub,
                "created_at": user.created_at.isoformat(),
            }
            for user in users
        ],
        "skip": skip,
        "limit": limit,
        "note": "For full user details (email, name, role), query Auth0 Management API"
    }
```

**Get user details** (`GET /api/admin/users/{user_id}`):

```python
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
    artworks_count = db.query(Artwork).filter(Artwork.seller_id == user_id).count()
    bids_count = db.query(Bid).filter(Bid.bidder_id == user_id).count()
    total_spent = (
        db.query(func.sum(Bid.amount))
        .filter(Bid.bidder_id == user_id, Bid.is_winning.is_(True))
        .scalar()
        or 0
    )

    return {
        "id": user.id,
        "auth0_sub": user.auth0_sub,
        "created_at": user.created_at.isoformat(),
        "stats": {
            "artworks_created": artworks_count,
            "bids_placed": bids_count,
            "total_spent": float(total_spent),
        },
        "note": "For email, name, and role, query Auth0 Management API"
    }
```

---

## Stage 7: Update Tests

### Objective
Update all tests to work with new Auth0-centric authentication.

### Files to Modify

#### 7.1 Update Test Fixtures in `backend/tests/conftest.py`

**Update user fixtures** to create minimal users:

```python
@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Create an admin user for testing."""
    user = User(auth0_sub="auth0|test-admin-123")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    # Attach Auth0 data (simulated)
    user.email = "admin@test.com"
    user.name = "Test Admin"
    user.role = "ADMIN"

    return user
```

**Update token generation** to include role in custom claim:

```python
def create_test_token(user: User) -> str:
    """Create a test JWT token with Auth0-style claims."""
    payload = {
        "sub": user.auth0_sub,
        "email": getattr(user, 'email', 'test@example.com'),
        "name": getattr(user, 'name', 'Test User'),
        "https://guesstheworth.demo/roles": [getattr(user, 'role', 'BUYER')],
        "exp": datetime.now(UTC) + timedelta(hours=1),
        "iat": datetime.now(UTC),
    }
    return JWTService.create_token(payload)
```

#### 7.2 Update Integration Tests

Search for all test files that reference:
- `user.email`
- `user.name`
- `user.role`

Make sure they're either:
1. Setting these attributes on the user object (they're not in DB anymore)
2. Or mocking Auth0 responses

---

## Stage 8: Frontend Updates (Optional)

### Objective
Update frontend to display user info from Auth0 tokens instead of API responses.

### Files to Modify

#### 8.1 Update User Context/Store

If the frontend stores user data, update it to read from the Auth0 token instead of `/api/users/me`.

#### 8.2 Update User Display Components

Any component showing user email/name should read from the Auth0 user object:

```javascript
import { useAuth0 } from '@auth0/auth0-react';

function UserProfile() {
  const { user } = useAuth0();

  return (
    <div>
      <p>Email: {user.email}</p>
      <p>Name: {user.name}</p>
      <p>Role: {user['https://guesstheworth.demo/roles'][0]}</p>
    </div>
  );
}
```

---

## Stage 9: Deployment & Migration

### Objective
Deploy changes and migrate production database.

### Steps

#### 9.1 Pre-Deployment: Set Up Auth0 Users

1. Create admin users in Auth0 Dashboard
2. Assign ADMIN role to admin users
3. Note their `auth0_sub` (user_id) values

#### 9.2 ⚠️ CRITICAL: Clear Production Database

**BEFORE deploying code changes**, you must clear all existing data due to incompatible user ID references.

**Option A: Direct Database Access**
```bash
# Connect to your Azure PostgreSQL database
psql "postgresql://username@server:password@server.postgres.database.azure.com:5432/dbname?sslmode=require"

# Clear all data (preserves schema)
TRUNCATE TABLE bids CASCADE;
TRUNCATE TABLE artworks CASCADE;
TRUNCATE TABLE users CASCADE;
```

**Option B: Via Admin API (if endpoint exists)**
```bash
# Get admin token first (using old authentication)
curl -X POST "https://your-backend.azurewebsites.net/api/admin/clear-database" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Verification**: After clearing, verify tables are empty but schema remains:
```sql
SELECT COUNT(*) FROM users;    -- Should return 0
SELECT COUNT(*) FROM artworks; -- Should return 0
SELECT COUNT(*) FROM bids;     -- Should return 0
```

#### 9.3 Deploy Backend Changes

1. Commit all code changes
2. Push to main branch
3. Wait for Azure deployment to complete

#### 9.4 Run Database Migration

Use the `/api/admin/run-migrations` endpoint:

```bash
# Login as admin (using Auth0 credentials)
TOKEN=$(curl -s -X POST "https://your-backend.azurewebsites.net/api/auth/token" \
  -H "Authorization: Bearer YOUR_AUTH0_TOKEN" | jq -r '.access_token')

# Run migrations
curl -X POST "https://your-backend.azurewebsites.net/api/admin/run-migrations" \
  -H "Authorization: Bearer $TOKEN"
```

#### 9.5 Verify Migration

Check that:
1. Users table only has `id`, `auth0_sub`, `created_at`
2. Admin can login via Auth0
3. Role-based access control works

---

## Stage 10: Cleanup

### Objective
Remove deprecated code and temporary workarounds.

### Files to Delete

1. `backend/routers/auth.py` - Email/password login endpoint
2. `backend/seeds/seed_production.sh` - Used bootstrap token
3. Any references to hardcoded admin credentials

### Files to Update

1. `backend/utils/auth.py` - Remove password hashing functions
2. `backend/routers/admin.py` - Remove bootstrap token logic
3. `README.md` - Update authentication documentation

### Environment Variables to Remove

From `.env` and Azure environment:
- Any variables related to JWT secrets for local auth (if using only Auth0)

---

## Rollback Plan

If something goes wrong, you can rollback:

### Database Rollback

```bash
alembic downgrade -1
```

This will restore the `email`, `name`, `role`, `password_hash` columns.

### Code Rollback

```bash
git revert <commit-hash>
git push origin main
```

---

## Testing Checklist

After implementation, verify:

- [ ] Admin user can login via Auth0
- [ ] Admin user can access admin endpoints
- [ ] Seller user can create artworks
- [ ] Buyer user can place bids
- [ ] Non-admin users cannot access admin endpoints
- [ ] User creation on first Auth0 login works
- [ ] Roles from Auth0 are correctly enforced
- [ ] Database only stores minimal user data
- [ ] All tests pass
- [ ] Frontend displays user info correctly

---

## Notes for Claude Code

When implementing this guide:

1. **Work in stages** - Complete one stage fully before moving to the next
2. **Run tests after each stage** - Ensure nothing breaks
3. **Create migration before modifying models** - Alembic needs the old model definition
4. **Update tests alongside code changes** - Don't leave tests for the end
5. **Ask for clarification** if Auth0 configuration details are unclear
6. **Backup before deploying** - Always have a rollback plan ready

## Test Migration Progress

### Completed Test Files (9/13)
- ✅ `backend/tests/conftest.py` - All fixtures updated
- ✅ `backend/tests/unit/test_models.py` - Model tests updated
- ✅ `backend/tests/unit/test_schemas.py` - Schema tests updated
- ✅ `backend/tests/unit/test_seeds.py` - Seed tests updated
- ✅ `backend/tests/unit/test_auth_service.py` - Auth service tests updated
- ✅ `backend/tests/integration/test_auth_api.py` - Auth API tests updated
- ✅ `backend/tests/integration/test_auth_fixes.py` - Partially updated
- ✅ `backend/tests/integration/test_artworks_api.py` - Partially updated
- ✅ `backend/tests/integration/test_bids_api.py` - Partially updated

### Remaining Test Files (4 files)

#### `backend/tests/integration/test_bids_api.py`
**Remaining UserRole references (5 occurrences):**
- Line 400, 410, 442, 449, 672: User creation with `UserRole.BUYER` and token generation

**Required changes:**
```python
# Replace patterns like:
buyer = User(auth0_sub="auth0|buyer", email="buyer@test.com", name="Buyer", role=UserRole.BUYER)

# With:
buyer = User(auth0_sub="auth0|buyer")
db_session.add(buyer)
db_session.commit()
db_session.refresh(buyer)
buyer.email = "buyer@test.com"
buyer.name = "Buyer"
buyer.role = "BUYER"

# And:
data={"sub": buyer.auth0_sub, "role": UserRole.BUYER.value}
# Becomes:
data={"sub": buyer.auth0_sub, "role": "BUYER"}
```

#### `backend/tests/integration/test_image_upload.py`
**Remaining UserRole references (2 occurrences):**
- Lines 101, 107: User creation and token generation

#### `backend/tests/integration/test_migrations.py`
**Remaining UserRole references (2 occurrences):**
- Lines 310, 325: User creation in test cases
- **Also needs:** Update import from `from models.user import User, UserRole` to `from models.user import User`

#### `backend/tests/integration/test_stats.py`
**Remaining UserRole references (2 occurrences):**
- Lines 129, 270: User creation in test cases
- **Also needs:** Update import statement

#### `backend/tests/integration/test_users_api.py`
**Remaining UserRole references (6 occurrences):**
- Lines 54, 76, 98, 120, 351, 372: User creation in multiple test methods
- **Also needs:** Remove `from models.user import UserRole` import

### How to Complete Remaining Tests

**Step-by-step for each file:**

1. **Remove UserRole import:**
   ```python
   # OLD:
   from models.user import User, UserRole

   # NEW:
   from models.user import User
   ```

2. **Update user creation pattern** everywhere:
   ```python
   # OLD:
   user = User(
       auth0_sub="auth0|test",
       email="test@example.com",
       name="Test User",
       role=UserRole.BUYER
   )

   # NEW:
   user = User(auth0_sub="auth0|test")
   db_session.add(user)
   db_session.commit()
   db_session.refresh(user)
   # Attach Auth0 data (simulated)
   user.email = "test@example.com"
   user.name = "Test User"
   user.role = "BUYER"
   ```

3. **Update JWT token generation:**
   ```python
   # OLD:
   token = JWTService.create_access_token(
       data={"sub": user.auth0_sub, "role": UserRole.BUYER.value}
   )

   # NEW:
   token = JWTService.create_access_token(
       data={"sub": user.auth0_sub, "role": "BUYER"}
   )
   ```

4. **Update role assertions:**
   ```python
   # OLD:
   assert user.role == UserRole.BUYER

   # NEW:
   assert user.role == "BUYER"
   ```

### Verification Commands

After completing updates, run:
```bash
cd backend

# Run all tests
pytest tests/ -v

# Or run specific test files
pytest tests/integration/test_bids_api.py -v
pytest tests/integration/test_image_upload.py -v
pytest tests/integration/test_migrations.py -v
pytest tests/integration/test_stats.py -v
pytest tests/integration/test_users_api.py -v

# Check for remaining UserRole references
grep -r "UserRole\." tests/ --include="*.py"
```

---

## Success Criteria

Migration is complete when:
1. ✅ Auth0 is the single source of truth for user data
2. ✅ Database only stores user references (id, auth0_sub)
3. ✅ Roles are managed in Auth0, not database
4. ✅ No hardcoded credentials in code
5. ⚠️ All tests pass (9/13 test files updated, 4 remaining)
6. ⏳ Production deployment successful (pending)
7. ⏳ Users can login and access features based on their Auth0 roles (pending)
