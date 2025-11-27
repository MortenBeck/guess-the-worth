# Contributing to Guess The Worth

Thank you for your interest in contributing to Guess The Worth! This document provides guidelines and instructions for contributing to the project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Security Considerations](#security-considerations)
- [Project Structure](#project-structure)

---

## Code of Conduct

This is an educational project developed for a DevOps course at DTU. We expect all contributors to:

- Be respectful and professional in all interactions
- Focus on constructive feedback and collaboration
- Help maintain a welcoming environment for learning

---

## Getting Started

### Prerequisites

- **Docker & Docker Compose** (recommended for easiest setup)
- **Python 3.11+** (for backend development)
- **Node.js 20+** (for frontend development)
- **PostgreSQL 15+** (if running without Docker)
- **Git** for version control

### Initial Setup

1. **Fork and Clone**

   ```bash
   git clone https://github.com/YOUR_USERNAME/guess-the-worth.git
   cd guess-the-worth
   ```

2. **Environment Configuration**

   ```bash
   # Backend
   cp backend/.env.example backend/.env
   # Edit backend/.env with your Auth0 credentials and database URL

   # Frontend
   cp frontend/.env.example frontend/.env
   # Edit frontend/.env with your Auth0 credentials and API URL
   ```

3. **Start with Docker** (Recommended)

   ```bash
   docker-compose up
   ```

4. **Or Run Locally**

   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt
   alembic upgrade head
   uvicorn main:socket_app --reload

   # Frontend (in separate terminal)
   cd frontend
   npm install
   npm run dev
   ```

### Verify Setup

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## Development Workflow

### Branch Strategy

We use a Git Flow-inspired workflow:

- `main` - Production-ready code
- `dev` - Development branch (default target for PRs)
- `feature/*` - New features (branch from `dev`)
- `bugfix/*` - Bug fixes (branch from `dev`)
- `hotfix/*` - Critical production fixes (branch from `main`)

### Creating a Feature Branch

```bash
git checkout dev
git pull origin dev
git checkout -b feature/your-feature-name
```

### Workflow Steps

1. Create a feature branch from `dev`
2. Make your changes
3. Write/update tests
4. Run tests locally
5. Commit with conventional commit messages
6. Push and create a Pull Request to `dev`
7. Address review feedback
8. Maintainer merges after approval

---

## Code Standards

### Backend (Python/FastAPI)

**Linting & Formatting:**

- **Black** for code formatting
- **isort** for import sorting
- **Bandit** for security checks

```bash
cd backend
black .
isort .
bandit -r . -c pyproject.toml
```

**Code Quality:**

- Follow PEP 8 style guide
- Use type hints for function signatures
- Maximum line length: 88 characters (Black default)
- Write docstrings for public functions and classes

**Example:**

```python
from typing import Optional
from pydantic import BaseModel

def get_artwork_by_id(artwork_id: int) -> Optional[Artwork]:
    """
    Retrieve an artwork by its ID.

    Args:
        artwork_id: The unique identifier of the artwork

    Returns:
        Artwork object if found, None otherwise
    """
    return db.query(Artwork).filter(Artwork.id == artwork_id).first()
```

### Frontend (React/JavaScript)

**Linting & Formatting:**

- **ESLint** for code quality
- **Prettier** for formatting

```bash
cd frontend
npm run lint
npm run format
```

**Code Quality:**

- Use functional components with hooks
- Follow React best practices
- Use TypeScript types where beneficial
- Keep components focused and reusable

**Example:**

```jsx
import { useState, useEffect } from "react";
import { useAuth } from "../hooks/useAuth";

export const ArtworkCard = ({ artwork }) => {
  const { user } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  // Component logic...

  return <Box>{/* JSX content */}</Box>;
};
```

### General Guidelines

- **No hardcoded secrets** - Use environment variables
- **No commented-out code** - Delete unused code
- **Meaningful variable names** - Be descriptive
- **DRY principle** - Don't Repeat Yourself (but don't over-abstract)
- **KISS principle** - Keep It Simple, Stupid

---

## Testing Requirements

All contributions must include appropriate tests. We maintain high test coverage standards.

### Backend Testing

**Test Suite:**

- Unit tests for business logic
- Integration tests for API endpoints
- E2E tests for critical user flows

```bash
cd backend
pytest --cov --cov-report=html
```

**Coverage Requirements:**

- Minimum 65% overall coverage (enforced by CI)
- New code should have 80%+ coverage

**Example Test:**

```python
def test_create_bid_success(client, auth_headers, sample_artwork):
    """Test successful bid creation."""
    response = client.post(
        "/api/bids/",
        json={"artwork_id": sample_artwork.id, "amount": 150.00},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["amount"] == 150.00
```

### Frontend Testing

**Test Suite:**

- Unit tests for utility functions
- Component tests with React Testing Library
- Store tests for Zustand state management

```bash
cd frontend
npm test -- --coverage
```

**Coverage Requirements:**

- 100% coverage for stores (enforced by CI)
- High coverage for critical components

**Example Test:**

```javascript
import { render, screen } from "@testing-library/react";
import { ArtworkCard } from "./ArtworkCard";

test("renders artwork card with title", () => {
  const artwork = { id: 1, title: "Test Art" };
  render(<ArtworkCard artwork={artwork} />);
  expect(screen.getByText("Test Art")).toBeInTheDocument();
});
```

### Running Tests

```bash
# All tests with coverage
npm test                # Frontend
pytest --cov           # Backend

# Watch mode during development
npm test -- --watch    # Frontend
pytest --watch         # Backend (requires pytest-watch)
```

---

## Commit Guidelines

We follow **Conventional Commits** specification for clear, semantic commit messages.

### Commit Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat:` - New feature
- `fix:` - Bug fix
- `test:` - Adding or updating tests
- `docs:` - Documentation changes
- `chore:` - Maintenance tasks (dependencies, configs)
- `refactor:` - Code changes that neither fix bugs nor add features
- `perf:` - Performance improvements
- `style:` - Code style changes (formatting, no logic change)
- `ci:` - CI/CD configuration changes

### Examples

```bash
feat(artworks): add image upload validation

Implement file type and size validation for artwork images.
Max size: 5MB. Allowed types: JPG, PNG, WebP.

Closes #42

---

fix(auth): resolve token expiration handling

Users were not redirected to login when tokens expired.
Added token refresh logic and expiration checks.

---

test(bids): add integration tests for bid creation

Covers successful bids, validation errors, and authorization.
Increases coverage to 72%.
```

### Tips

- Use present tense ("add" not "added")
- Keep subject line under 72 characters
- Reference issue numbers when applicable
- Explain "why" in the body, not just "what"

---

## Pull Request Process

### Before Submitting

1. **Update your branch**

   ```bash
   git checkout dev
   git pull origin dev
   git checkout your-branch
   git rebase dev
   ```

2. **Run all checks locally**

   ```bash
   # Backend
   cd backend
   black .
   isort .
   pytest --cov
   bandit -r . -c pyproject.toml

   # Frontend
   cd frontend
   npm run lint
   npm run format
   npm test -- --coverage
   ```

3. **Ensure tests pass**
   - All existing tests pass
   - New tests added for new functionality
   - Coverage thresholds met

### PR Template

When creating a PR, include:

**Title:** Follow conventional commit format

```
feat(artworks): add category filtering
```

**Description:**

```markdown
## Summary

Brief description of changes

## Changes Made

- Added category filter dropdown
- Updated API endpoint to support category parameter
- Added tests for category filtering

## Testing

- [ ] Backend tests pass
- [ ] Frontend tests pass
- [ ] Manual testing completed
- [ ] No new console errors

## Screenshots (if UI changes)

[Attach screenshots]

## Related Issues

Closes #123
```

### Review Process

1. **Automated Checks** - CI/CD pipeline runs:
   - Code quality (linting, formatting)
   - Security scans (Bandit, TruffleHog, Trivy)
   - Test suites
   - Coverage reports

2. **Code Review** - Maintainers will:
   - Review code quality and architecture
   - Check test coverage
   - Verify security considerations
   - Provide feedback

3. **Required Approvals** - Typically 1 approval from maintainers

4. **Merge** - Maintainer squashes and merges to `dev`

### After Merge

- Delete your feature branch
- Pull latest `dev` changes
- Monitor CI/CD pipeline for any issues

---

## Security Considerations

**This is critical:** Always follow security best practices when contributing.

### Required Reading

- Review [SECURITY.md](SECURITY.md) for known vulnerabilities
- Never introduce new security issues

### Security Checklist

Before submitting your PR, verify:

- [ ] No hardcoded secrets or API keys
- [ ] All sensitive data in environment variables
- [ ] User input is validated (Pydantic/Zod)
- [ ] Authorization checks are present
- [ ] SQL injection prevented (use SQLAlchemy ORM)
- [ ] XSS prevented (React escapes by default)
- [ ] CSRF tokens used for state-changing operations
- [ ] Rate limiting on public endpoints
- [ ] Proper error messages (no sensitive info leaked)

### Authentication & Authorization

**Never trust client input for identity:**

```python
# ❌ BAD - User can manipulate query parameter
@router.post("/bids/")
def create_bid(bidder_id: int, amount: float):
    # Anyone can bid as anyone!
    pass

# ✅ GOOD - Extract user from verified JWT token
@router.post("/bids/")
def create_bid(amount: float, current_user: User = Depends(get_current_user)):
    # User identity verified from token
    pass
```

### Reporting Security Issues

If you discover a security vulnerability:

- **DO NOT** open a public issue
- Report via GitHub Security Advisories
- See [SECURITY.md](SECURITY.md) for details

---

## Project Structure

### Backend Structure

```
backend/
├── alembic/              # Database migrations
│   └── versions/         # Migration files
├── config/
│   └── settings.py       # Configuration and environment variables
├── middleware/
│   ├── rate_limit.py     # Rate limiting middleware
│   └── security_headers.py
├── models/
│   ├── artwork.py        # SQLAlchemy models
│   ├── bid.py
│   ├── user.py
│   └── audit_log.py
├── routers/              # API endpoints
│   ├── artworks.py
│   ├── bids.py
│   ├── auth.py
│   ├── users.py
│   ├── admin.py
│   ├── stats.py
│   └── health.py
├── schemas/              # Pydantic schemas
│   ├── artwork.py
│   ├── bid.py
│   └── user.py
├── services/             # Business logic
│   ├── auth_service.py
│   └── auction_service.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── database.py           # Database connection
├── main.py               # FastAPI app & Socket.IO
└── requirements.txt
```

### Frontend Structure

```
frontend/
├── public/               # Static assets
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── ArtworkCard.jsx
│   │   ├── BidForm.jsx
│   │   └── ...
│   ├── pages/            # Route pages
│   │   ├── HomePage.jsx
│   │   ├── ArtworkDetailPage.jsx
│   │   └── ...
│   ├── store/            # Zustand state management
│   │   ├── authStore.js
│   │   ├── artworkStore.js
│   │   └── bidStore.js
│   ├── services/         # API client
│   │   ├── api.js
│   │   └── socket.js
│   ├── hooks/            # Custom React hooks
│   │   ├── useAuth.js
│   │   └── useWebSocket.js
│   ├── utils/            # Utility functions
│   ├── config/           # Configuration
│   ├── theme/            # Chakra UI theme
│   ├── test/             # Test utilities
│   ├── App.jsx           # Main app component
│   └── main.jsx          # Entry point
├── package.json
└── vite.config.js
```

### Key Files to Know

**Backend:**

- [main.py](backend/main.py) - FastAPI app initialization, Socket.IO setup
- [database.py](backend/database.py) - Database connection and session management
- [config/settings.py](backend/config/settings.py) - Environment configuration

**Frontend:**

- [App.jsx](frontend/src/App.jsx) - Main app component with routing
- [main.jsx](frontend/src/main.jsx) - React entry point
- [services/api.js](frontend/src/services/api.js) - API client setup

---

## Development Tips

### Database Migrations

**Creating a migration:**

```bash
cd backend
alembic revision --autogenerate -m "Add artwork category field"
alembic upgrade head
```

**Rolling back:**

```bash
alembic downgrade -1
```

### Debugging

**Backend:**

```python
import pdb; pdb.set_trace()  # Python debugger
```

**Frontend:**

```javascript
console.log("Debug:", variable); // Browser console
debugger; // Browser debugger
```

### Environment Variables

Both backend and frontend use `.env` files. Never commit these files.

**Backend** (`.env`):

```
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
AUTH0_DOMAIN=your-domain.auth0.com
AUTH0_CLIENT_ID=your-client-id
AUTH0_CLIENT_SECRET=your-secret
JWT_SECRET_KEY=your-jwt-secret
SENTRY_DSN=your-sentry-dsn
```

**Frontend** (`.env`):

```
VITE_AUTH0_DOMAIN=your-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_API_URL=http://localhost:8000
```

### Common Issues

**Database connection errors:**

- Verify PostgreSQL is running
- Check DATABASE_URL in `.env`
- Run migrations: `alembic upgrade head`

**Auth0 errors:**

- Verify credentials in `.env`
- Check Auth0 dashboard configuration
- Ensure callback URLs are configured

**Port conflicts:**

- Frontend default: 5173 (configurable in `vite.config.js`)
- Backend default: 8000 (pass `--port` to uvicorn)

---

## Getting Help

- **Documentation:** Check [README.md](README.md) for overview
- **Issues:** Search existing issues before creating new ones
- **Discussions:** Use GitHub Discussions for questions
- **Security:** Report security issues privately via [SECURITY.md](SECURITY.md)

---

## Recognition

Contributors will be recognized in our [CHANGELOG.md](CHANGELOG.md) and commit history. Thank you for helping make Guess The Worth better!

---

**Last Updated:** 2025-11-24
