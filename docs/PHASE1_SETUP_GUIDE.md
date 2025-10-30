# Phase 1: Foundation Setup Guide

This guide walks you through setting up the development foundation for CI/CD.

## 📋 Overview

Phase 1 establishes:
- ✅ Backend linting and formatting tools
- ✅ Comprehensive test suite structure
- ✅ Pre-commit hooks for code quality
- ✅ Initial test coverage

## 🔧 Installation Steps

### 1. Install Backend Development Dependencies

```bash
cd backend
pip install -r requirements.txt
```

New dependencies added:
- `black` - Code formatter
- `flake8` - Linter
- `mypy` - Type checker
- `isort` - Import sorter
- `pytest-cov` - Coverage reporting
- `faker` - Test data generation

### 2. Install Pre-commit Hooks

```bash
# From project root
pip install pre-commit
pre-commit install
```

This installs git hooks that will automatically run on every commit.

### 3. Verify Setup

```bash
# Test backend linting
cd backend
black --check .
flake8 .
isort --check-only .

# Run backend tests
pytest

# Run backend tests with coverage
pytest --cov=. --cov-report=html
```

```bash
# Test frontend
cd frontend
npm test
```

## 📁 What Was Created

### Backend Configuration Files

#### [backend/pyproject.toml](../backend/pyproject.toml)
Configuration for:
- Black (code formatting)
- isort (import sorting)
- mypy (type checking)
- pytest (testing)

#### [backend/.flake8](../backend/.flake8)
Flake8 linting rules and exclusions.

### Test Structure

```
backend/tests/
├── __init__.py
├── conftest.py           # Pytest fixtures and setup
├── test_auth.py          # Authentication endpoint tests
├── test_artworks.py      # Artwork CRUD tests
├── test_bids.py          # Bidding logic tests
└── test_database.py      # Database model tests
```

```
frontend/src/components/
├── __tests__/
│   └── Header.test.jsx
└── home/
    └── __tests__/
        └── LiveAuctions.test.jsx
```

### Pre-commit Configuration

#### [.pre-commit-config.yaml](../.pre-commit-config.yaml)
Automated checks on every commit:
- Trailing whitespace removal
- End-of-file fixing
- YAML/JSON validation
- Large file detection
- Secret detection
- Python: black, isort, flake8
- JavaScript: ESLint

## 🧪 Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=term-missing

# Run specific test file
pytest tests/test_auth.py

# Run specific test
pytest tests/test_auth.py::TestAuthEndpoints::test_register_new_user

# Run with verbose output
pytest -v

# Generate HTML coverage report
pytest --cov=. --cov-report=html
# Open htmlcov/index.html in browser
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Run tests with coverage
npm test -- --coverage

# Run tests with UI
npm run test:ui
```

## 🎨 Code Formatting

### Backend

```bash
cd backend

# Format code with black
black .

# Sort imports with isort
isort .

# Check code with flake8
flake8 .

# Type check with mypy
mypy .

# Format everything at once
black . && isort . && flake8 .
```

### Frontend

```bash
cd frontend

# Lint and fix
npm run lint

# Just check (no fix)
npx eslint src/
```

## 🔍 Pre-commit Hook Usage

Once installed, pre-commit hooks run automatically on `git commit`:

```bash
# Regular commit - hooks run automatically
git add .
git commit -m "Add new feature"

# Skip hooks (not recommended)
git commit -m "Quick fix" --no-verify

# Run hooks manually on all files
pre-commit run --all-files

# Update hooks to latest versions
pre-commit autoupdate
```

## 📊 Test Coverage

### Current Test Coverage

**Backend:**
- ✅ Authentication endpoints (register, login, get user)
- ✅ Artwork CRUD operations
- ✅ Bidding logic and threshold validation
- ✅ Database models and relationships
- ⏳ Socket.IO events (to be added)
- ⏳ File upload (to be added)

**Frontend:**
- ✅ Header component (authenticated/unauthenticated states)
- ✅ LiveAuctions component (data loading and display)
- ⏳ Additional components (to be added)

### Adding New Tests

#### Backend Test Example

```python
# backend/tests/test_new_feature.py
import pytest
from fastapi import status

class TestNewFeature:
    def test_something(self, client, db_session):
        """Test description."""
        response = client.get("/api/endpoint")
        assert response.status_code == status.HTTP_200_OK
```

#### Frontend Test Example

```javascript
// frontend/src/components/__tests__/MyComponent.test.jsx
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import MyComponent from '../MyComponent'

describe('MyComponent', () => {
  it('renders correctly', () => {
    render(<MyComponent />)
    expect(screen.getByText('Expected Text')).toBeInTheDocument()
  })
})
```

## 🐛 Troubleshooting

### Pre-commit Hook Failures

**Problem:** Black/flake8 fails on commit
```bash
# Fix formatting issues
cd backend
black .
isort .

# Then commit again
git add .
git commit -m "Your message"
```

**Problem:** ESLint fails on commit
```bash
cd frontend
npm run lint

# Then commit again
```

### Test Failures

**Problem:** Tests fail with database errors
```bash
# Tests use in-memory SQLite, ensure you're not modifying global DB config
# Check backend/tests/conftest.py for proper isolation
```

**Problem:** Frontend tests can't find modules
```bash
# Ensure all dependencies are installed
cd frontend
npm install
```

### Import Errors

**Problem:** `ModuleNotFoundError` in tests
```bash
# Make sure you're running from the correct directory
cd backend
pytest

# Or use absolute imports in test files
```

## ✅ Next Steps

After completing Phase 1, you're ready for:

**Phase 2: GitHub Actions CI Workflow**
- Automated testing on every push/PR
- Code coverage reporting
- Build verification

**Phase 3: Docker & Containerization**
- Production-ready Dockerfiles
- Multi-stage builds
- Container security scanning

**Phase 4: Continuous Deployment**
- Automated deployments to staging/production
- Database migration automation
- Health checks and rollback procedures

## 📚 Resources

- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Pre-commit Documentation](https://pre-commit.com/)
- [Testing Library](https://testing-library.com/)

---

**Need Help?** Check the main [CI/CD Guide](./CI_CD_GUIDE.md) or open an issue.
