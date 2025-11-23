# Test Fix Plan - Session Breakdown

**Created:** 2025-11-23
**Status:** Ready to Execute
**Goal:** Fix 41 failing tests by adding authentication headers

---

## 📋 Quick Summary

**Problem:** Tests fail because they don't include authentication headers
**Solution:** Add `headers={"Authorization": f"Bearer {token}"}` to requests
**Estimated Total Time:** 2-3 hours across 2-3 sessions

---

## Session 1: Rate Limiting & Audit Tests (30-45 min)

**Goal:** Fix the clearest pattern cases first

### Files to Fix:
1. `tests/integration/test_rate_limiting.py` (2 tests)
2. `tests/integration/test_audit_logging.py` (5 tests)

### Instructions:

**For test_rate_limiting.py:**
```python
# Pattern: Add buyer_token or seller_token to function signature
# Add headers to all client.post() calls

# Line 38: Update function signature
def test_rate_limiting_on_bid_creation(client: TestClient, artwork, buyer_user, buyer_token):

# Lines 45-51: Add headers parameter
response = client.post(
    "/api/bids/",
    json={"artwork_id": artwork.id, "amount": 100 + i},
    headers={"Authorization": f"Bearer {buyer_token}"}  # ADD THIS
)

# Line 64: Update function signature
def test_rate_limiting_on_artwork_creation(client: TestClient, seller_user, seller_token):

# Lines 71-77: Add headers parameter
response = client.post(
    "/api/artworks/",
    json={"title": f"Test Artwork {i}", "description": "Test description", "secret_threshold": 1000},
    headers={"Authorization": f"Bearer {seller_token}"}  # ADD THIS
)
```

**For test_audit_logging.py:**
- Find all `client.post()` calls
- Add `buyer_token` or `seller_token` to function signatures
- Add `headers={"Authorization": f"Bearer {token}"}` to each request

### Validation:
```bash
cd backend
pytest tests/integration/test_rate_limiting.py -v
pytest tests/integration/test_audit_logging.py -v
# Should show 7/7 passing
```

---

## Session 2: Auth Tests (45-60 min)

**Goal:** Fix auth-specific tests and update 403/401 expectations

### Files to Fix:
1. `tests/integration/test_auth_fixes.py` (10 tests)
2. `tests/integration/test_auth_api.py` (6 tests)

### Special Instructions:

**For test_auth_fixes.py:**
These tests are checking that endpoints REQUIRE auth, so they should expect 403 (not 401) when no auth is provided.

```python
# Tests that check "requires_auth" should expect 403
def test_create_artwork_requires_auth(client: TestClient):
    response = client.post("/api/artworks/", json={...})
    assert response.status_code == 403  # Changed from 401

# Tests that provide bad tokens should expect 401
def test_invalid_token_rejected(client: TestClient):
    response = client.post(
        "/api/artworks/",
        json={...},
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401  # This stays 401
```

**For test_auth_api.py:**
Some tests need tokens, some test missing tokens:

```python
# Tests checking user retrieval - ADD token
def test_get_current_user_success(client: TestClient, buyer_user, buyer_token):
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert response.status_code == 200

# Tests checking missing auth - EXPECT 403
def test_get_current_user_missing_auth0_sub(client: TestClient):
    response = client.get("/api/auth/me")  # No token
    assert response.status_code == 403  # Changed from 401 or 422
```

### Validation:
```bash
pytest tests/integration/test_auth_fixes.py -v
pytest tests/integration/test_auth_api.py -v
# Should show 16/16 passing
```

---

## Session 3: Integration & E2E Tests (60-90 min)

**Goal:** Fix remaining integration and E2E tests

### Files to Fix:
1. `tests/integration/test_artworks_api.py` (7 tests)
2. `tests/integration/test_image_upload.py` (1 test)
3. `tests/integration/test_stats.py` (2 tests)
4. `tests/e2e/test_complete_flow.py` (7 tests)

### Instructions:

**For integration tests:**
Pattern is the same - add appropriate token fixtures:

```python
# Before
def test_create_artwork_missing_required_fields(client: TestClient):
    response = client.post("/api/artworks/", json={...})

# After
def test_create_artwork_missing_required_fields(client: TestClient, seller_user, seller_token):
    response = client.post(
        "/api/artworks/",
        json={...},
        headers={"Authorization": f"Bearer {seller_token}"}
    )
```

**For E2E tests:**
These are more complex - they simulate full user flows. You'll need to:
1. Add token fixtures (buyer_token, seller_token, admin_token)
2. Add headers to EVERY authenticated request in the flow
3. Some tests create multiple users - need multiple tokens

Example pattern:
```python
def test_buyer_registration_to_winning_bid_flow(client, db_session):
    # 1. Register buyer
    buyer_response = client.post("/api/auth/register", json={...})
    buyer_data = buyer_response.json()

    # 2. Create token for this buyer
    from services.jwt_service import JWTService
    buyer_token = JWTService.create_access_token(
        data={"sub": buyer_data["auth0_sub"], "role": "BUYER"}
    )

    # 3. Browse artworks (no auth needed)
    artworks = client.get("/api/artworks/").json()

    # 4. Place bid (needs auth)
    bid_response = client.post(
        "/api/bids/",
        json={"artwork_id": artworks[0]["id"], "amount": 500},
        headers={"Authorization": f"Bearer {buyer_token}"}  # ADD THIS
    )
```

### Validation:
```bash
pytest tests/integration/test_artworks_api.py -v
pytest tests/integration/test_image_upload.py -v
pytest tests/integration/test_stats.py -v
pytest tests/e2e/test_complete_flow.py -v
# Should show 17/17 passing
```

---

## Final Validation (5-10 min)

After all sessions complete:

```bash
cd backend

# Run full test suite
pytest -v

# Expected output:
# ====== 314 passed, 13 skipped in X.XXs ======

# Check coverage
pytest --cov=. --cov-report=term-missing

# Expected: Coverage should be ~65-70% overall
```

---

## Quick Reference: Token Fixtures

Available in `conftest.py`:

```python
buyer_token    # For BUYER role tests
seller_token   # For SELLER role tests
admin_token    # For ADMIN role tests
```

All generate valid JWT tokens that work with the authentication system.

---

## Common Patterns

### Pattern 1: Simple Authenticated Request
```python
def test_something(client, buyer_user, buyer_token):
    response = client.post(
        "/api/endpoint/",
        json={...},
        headers={"Authorization": f"Bearer {buyer_token}"}
    )
    assert response.status_code == 200
```

### Pattern 2: Test Expects Auth Failure
```python
def test_requires_auth(client):
    response = client.post("/api/endpoint/", json={...})
    assert response.status_code == 403  # No auth header
```

### Pattern 3: Test Invalid Token
```python
def test_invalid_token(client):
    response = client.post(
        "/api/endpoint/",
        json={...},
        headers={"Authorization": "Bearer invalid"}
    )
    assert response.status_code == 401  # Bad token format valid, content invalid
```

---

## Troubleshooting

**If a test still fails after adding headers:**

1. Check the token matches the user role needed:
   - Artwork creation → seller_token
   - Bid creation → buyer_token
   - Admin endpoints → admin_token

2. Check the user fixture is included:
   - `buyer_token` needs `buyer_user`
   - `seller_token` needs `seller_user`
   - `admin_token` needs `admin_user`

3. Verify the endpoint path is correct

4. Check if test expects 403 or 401:
   - No auth header → 403
   - Invalid token → 401

---

## Git Workflow

```bash
# Before starting
git checkout dev
git pull origin dev

# Start Session 1
git checkout -b fix/test-auth-session-1
# ... make changes ...
git add tests/integration/test_rate_limiting.py tests/integration/test_audit_logging.py
git commit -m "fix: add auth headers to rate limiting and audit tests"

# Start Session 2
git checkout -b fix/test-auth-session-2
# ... make changes ...
git add tests/integration/test_auth_fixes.py tests/integration/test_auth_api.py
git commit -m "fix: add auth headers to auth tests and update 403 expectations"

# Start Session 3
git checkout -b fix/test-auth-session-3
# ... make changes ...
git add tests/integration/test_artworks_api.py tests/integration/test_image_upload.py tests/integration/test_stats.py tests/e2e/test_complete_flow.py
git commit -m "fix: add auth headers to integration and E2E tests"

# After all sessions pass
git checkout dev
git merge fix/test-auth-session-1 --no-ff
git merge fix/test-auth-session-2 --no-ff
git merge fix/test-auth-session-3 --no-ff
git push origin dev
```

---

## Success Criteria

- [ ] Session 1 complete: 7 tests passing
- [ ] Session 2 complete: 16 tests passing
- [ ] Session 3 complete: 17 tests passing
- [ ] Full suite: 314 tests passing, 13 skipped
- [ ] No new test failures introduced
- [ ] Coverage remains ~65% or improves

---

**Next Steps After Completion:**
1. Update testing_summary.md with new test counts
2. Run security scans (pip-audit, bandit)
3. Consider fixing deprecation warnings (optional)
4. Deploy to staging for validation
