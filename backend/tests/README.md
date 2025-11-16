# Backend Testing Suite

Comprehensive test suite for the Guess The Worth backend API.

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and test configuration
├── unit/                       # Unit tests (models, schemas, services)
│   ├── test_schemas.py        # Pydantic schema validation tests
│   ├── test_models.py         # SQLAlchemy model tests
│   └── test_auth_service.py   # Authentication service tests
├── integration/               # API integration tests
│   ├── test_auth_api.py      # /api/auth endpoints
│   ├── test_artworks_api.py  # /api/artworks endpoints
│   ├── test_bids_api.py      # /api/bids endpoints (critical threshold logic)
│   └── test_users_api.py     # /api/users endpoints
└── e2e/                      # End-to-end workflow tests
    └── test_complete_flow.py # Full user journey tests

```

## Running Tests

### Run All Tests
```bash
cd backend
pytest
```

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# E2E tests only
pytest tests/e2e/

# Specific test file
pytest tests/integration/test_bids_api.py

# Specific test class
pytest tests/integration/test_bids_api.py::TestBidThresholdLogic

# Specific test function
pytest tests/integration/test_bids_api.py::TestBidThresholdLogic::test_only_threshold_bids_win
```

### Run with Coverage Report
```bash
# Terminal report
pytest --cov=. --cov-report=term-missing

# HTML report
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser

# XML report (for CI/CD)
pytest --cov=. --cov-report=xml
```

### Run with Verbose Output
```bash
pytest -v

# Very verbose with test output
pytest -vv -s
```

### Run Failed Tests Only
```bash
# Run only tests that failed last time
pytest --lf

# Run failed tests first, then others
pytest --ff
```

### Run Tests in Parallel (faster)
```bash
# Install pytest-xdist first: pip install pytest-xdist
pytest -n auto
```

## Test Coverage Goals

| Category | Target Coverage | Current Status |
|----------|----------------|----------------|
| Critical Paths (auth, bids) | >90% | ✅ Comprehensive |
| API Endpoints | >85% | ✅ All covered |
| Models & Schemas | >80% | ✅ Fully tested |
| Overall | >80% | 🔄 Run tests to check |

## Key Test Scenarios

### Critical Path Tests (Must Pass)

1. **Bid Threshold Logic** (`test_bids_api.py`)
   - Bid below threshold → not winning
   - Bid at threshold → winning, artwork sold
   - Bid above threshold → winning, artwork sold
   - Cannot bid on sold artwork

2. **Authentication Flow** (`test_auth_api.py`)
   - User registration with Auth0
   - JWT token verification
   - Role-based access control

3. **E2E Purchase Flow** (`test_complete_flow.py`)
   - User registers → creates artwork → places bids → wins auction

### Edge Cases Tested

- Negative bid amounts (rejected)
- Concurrent bidding from multiple users
- Bidding on non-existent artworks
- Duplicate user registration
- Unicode characters in user/artwork data
- Very large numbers and decimal precision
- Pagination boundary conditions

## Fixtures Available

From `conftest.py`:

### User Fixtures
- `buyer_user` - Test buyer user
- `seller_user` - Test seller user
- `admin_user` - Test admin user

### Artwork Fixtures
- `artwork` - Active artwork with threshold=100.0
- `sold_artwork` - Already sold artwork

### Bid Fixtures
- `bid` - Sample bid on artwork

### Auth Fixtures
- `buyer_token` - Valid JWT for buyer
- `seller_token` - Valid JWT for seller
- `admin_token` - Valid JWT for admin
- `mock_auth0_response` - Factory for Auth0 user data
- `auth_headers` - Authorization headers helper

### Database Fixtures
- `db_session` - Fresh database session (in-memory SQLite)
- `client` - FastAPI test client with DB override

## Writing New Tests

### Example Unit Test
```python
def test_user_create_valid(self):
    """Test UserCreate with valid data."""
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "auth0_sub": "auth0|123456",
        "role": UserRole.BUYER
    }
    user = UserCreate(**user_data)
    assert user.email == "test@example.com"
```

### Example Integration Test
```python
def test_create_bid_at_threshold(self, client, db_session, artwork, buyer_user):
    """Test creating bid exactly at secret_threshold (winning)."""
    payload = {
        "artwork_id": artwork.id,
        "amount": 100.0  # Exactly at threshold
    }

    response = client.post(
        f"/api/bids?bidder_id={buyer_user.id}",
        json=payload
    )

    assert response.status_code == 200
    assert response.json()["is_winning"] is True
```

### Example E2E Test
```python
def test_complete_user_flow(self, client):
    """Test complete flow from registration to purchase."""
    # 1. Register buyer
    buyer = client.post("/api/auth/register", json={...}).json()

    # 2. Register seller
    seller = client.post("/api/auth/register", json={...}).json()

    # 3. Create artwork
    artwork = client.post(f"/api/artworks?seller_id={seller['id']}", json={...}).json()

    # 4. Place winning bid
    bid = client.post(f"/api/bids?bidder_id={buyer['id']}", json={...}).json()

    # 5. Verify sold
    assert bid["is_winning"] is True
```

## Continuous Integration

Tests are automatically run on:
- Every push to main branch
- Every pull request
- Before deployment

See `.github/workflows/test.yml` for CI configuration.

## Test Database

- Uses **SQLite in-memory** database for speed
- Each test gets a fresh database (isolated)
- No need to clean up test data
- Production uses PostgreSQL

## Mocking Strategy

### What We Mock
- Auth0 API calls (`verify_auth0_token`)
- External HTTP requests
- File uploads (stub implementation)

### What We Don't Mock
- Database operations (use test DB)
- FastAPI endpoints (use TestClient)
- Business logic

## Common Issues

### Issue: Import errors
**Solution**: Make sure you're in the backend directory
```bash
cd backend
pytest
```

### Issue: Database errors
**Solution**: Ensure SQLite is available (built into Python)

### Issue: Slow tests
**Solution**: Run in parallel
```bash
pytest -n auto
```

### Issue: Coverage not showing
**Solution**: Make sure pytest-cov is installed
```bash
pip install pytest-cov
```

## Adding Tests for New Features

When adding a new feature:

1. **Write unit tests** for new models/schemas
2. **Write integration tests** for new API endpoints
3. **Update E2E tests** if workflow changes
4. **Aim for >80% coverage** for new code
5. **Include edge cases** (negative values, missing data, etc.)

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [FastAPI testing guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
