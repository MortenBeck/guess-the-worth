# Quick Test Reference Guide

## Run All Tests
```bash
cd backend
pytest
```

## Run Specific Test Categories
```bash
pytest tests/unit/                    # Unit tests only
pytest tests/integration/              # Integration tests only
pytest tests/e2e/                     # E2E tests only
```

## Run Critical Tests
```bash
# Test bid threshold logic (MOST IMPORTANT)
pytest tests/integration/test_bids_api.py::TestBidThresholdLogic -v

# Test complete user flow
pytest tests/e2e/test_complete_flow.py::TestCompleteUserFlow -v
```

## Coverage
```bash
# Terminal report
pytest --cov=. --cov-report=term-missing

# HTML report (detailed)
pytest --cov=. --cov-report=html
# Then open: htmlcov/index.html
```

## Debugging
```bash
# Verbose output
pytest -vv -s

# Run only failed tests
pytest --lf

# Run specific test
pytest tests/integration/test_bids_api.py::TestCreateBid::test_create_bid_at_threshold -v
```

## Fast Testing
```bash
# Install parallel testing
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

## Test Coverage Goals
- **Critical paths** (auth, bidding): >90%
- **API endpoints**: >85%
- **Models & schemas**: >80%
- **Overall**: >80%

## What's Tested
✅ Bid threshold logic (below/at/above threshold)
✅ User authentication (Auth0 + JWT)
✅ Artwork CRUD operations
✅ Concurrent bidding scenarios
✅ Database relationships & cascades
✅ Input validation & edge cases
✅ Complete user journeys (E2E)

## Troubleshooting

**Import errors**:
```bash
# Ensure you're in backend directory
cd backend
pytest
```

**Database errors**:
- Tests use SQLite in-memory (no setup needed)
- Each test gets fresh database

**Slow tests**:
```bash
# Run in parallel
pytest -n auto
```

For full documentation, see: `backend/tests/README.md`
