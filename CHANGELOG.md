# Changelog

All notable changes to Guess The Worth project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Comprehensive project documentation (CONTRIBUTING.md, CHANGELOG.md, architecture docs)

### Changed
- Updated dependency versions via Dependabot

### Fixed
- Health check endpoints now support HEAD requests for UptimeRobot monitoring compatibility

### Security
- Known security vulnerabilities documented in SECURITY.md
- All critical security issues remain unfixed (see SECURITY.md for details)

---

## [0.9.0] - 2025-11-23

### Major Achievement: Test Infrastructure Complete
This release represents a major milestone with comprehensive test coverage and CI/CD pipeline fully operational. **380 tests passing** across backend and frontend.

### Added

#### Testing & Quality Assurance
- **Test Infrastructure** - Complete testing suite with 380 passing tests
  - Backend: 50/51 tests passing (unit, integration, e2e)
  - Frontend: 92/92 tests passing
- **Code Coverage** - Backend 65%, Frontend 100% (stores)
- **Coverage Enforcement** - CI/CD fails if coverage drops below thresholds
- **Test Fixtures** - Comprehensive fixtures for database, auth, and test data
- **Migration Tests** - Automated rollback tests for database migrations

#### CI/CD Pipeline
- **GitHub Actions Workflows** - Comprehensive automation
  - Backend tests, linting (Black, isort, Bandit)
  - Frontend tests, linting (ESLint, Prettier)
  - Code coverage reporting (Codecov)
  - Security scanning (Trivy, TruffleHog, npm audit, pip-audit)
  - Docker build validation
  - Automated deployment to Azure
- **Dependabot** - Automated dependency updates with PR grouping
  - Daily security updates
  - Weekly version updates
  - Separate groups for production and development dependencies

#### Security & Monitoring
- **Health Monitoring** - Multiple health check endpoints
  - `/health` - Basic application health
  - `/health/db` - Database connectivity
  - `/api/admin/system/health` - System status (admin only)
- **Custom Health Dashboard** - Real-time service monitoring (health-dashboard.html)
- **UptimeRobot Integration** - External monitoring with status badges
- **Sentry Integration** - Error tracking and performance monitoring
- **Audit Logging** - Complete action logging for security events
- **Security Headers** - CSP, XSS protection, HSTS, frame options
- **Rate Limiting** - Protection on authentication and critical endpoints

#### Backend Features
- **Admin Dashboard** - User management, artwork oversight, system statistics
- **Statistics API** - Platform-wide, seller, and user-specific stats
- **Image Upload** - File validation, size limits, format checking
- **Auction Expiration** - Time-based auctions with automatic closure
- **Performance Optimization**
  - Database indexes on foreign keys and frequently queried fields
  - Pagination with configurable limits (default 10, max 100)
  - Eager loading to prevent N+1 query issues
- **Database Migrations** - Alembic migrations with idempotent initial migration

#### Frontend Features
- **Real-time Updates** - WebSocket bidding updates via Socket.IO
- **Admin Panel** - User management interface
- **Statistics Dashboard** - User, seller, and platform stats
- **Responsive Design** - Mobile-friendly UI with Chakra UI
- **Error Boundaries** - Graceful error handling

### Fixed
- **Test Infrastructure Issues** - Resolved authentication header issues in tests
- **Migration Idempotency** - Made initial migration idempotent for enum types
- **Frontend Build** - Fixed ESLint and Prettier issues
- **Docker Builds** - Resolved frontend and backend Docker build issues
- **Coverage Reporting** - Fixed Codecov integration

### Changed
- **Branch Strategy** - Implemented `main` (production) and `dev` (development) workflow
- **Code Quality Standards** - Enforced Black, isort, ESLint, Prettier
- **Test Organization** - Structured tests into unit, integration, and e2e categories
- **Environment Configuration** - All secrets moved to environment variables

### Security
- **Environment Variables** - All secrets removed from code and moved to `.env` files
- **Secret Scanning** - TruffleHog integrated in CI/CD pipeline
- **Vulnerability Scanning** - Trivy for containers, npm audit, pip-audit for dependencies
- **Security Analysis** - Comprehensive security audit completed (see SECURITY.md)

---

## [0.8.0] - 2025-11-21

### Added - Stage 10: Real-time Bidding
- **WebSocket Integration** - Socket.IO for real-time bid updates
- **Event Broadcasting** - Real-time notifications to all connected clients
- **Connection Management** - Graceful WebSocket connection handling
- **Frontend Socket Client** - React hooks for WebSocket communication

---

## [0.7.0] - 2025-11-20

### Added - Stage 9: Performance Optimization
- **Eager Loading** - Prevent N+1 query issues with `joinedload`
- **Database Indexes** - Indexes on foreign keys and frequently queried fields
- **Query Optimization** - Optimized SQLAlchemy queries
- **Performance Tests** - Integration tests for query performance

---

## [0.6.0] - 2025-11-19

### Added - Stage 8: Pagination & Rate Limiting
- **Pagination** - Configurable pagination for all list endpoints
  - Default limit: 10 items
  - Maximum limit: 100 items
  - Offset-based pagination
- **Rate Limiting** - Middleware to prevent abuse
  - 10 requests per minute for auth endpoints
  - 100 requests per minute for general API
  - Sliding window algorithm
- **Rate Limit Tests** - Integration tests for rate limiting behavior

---

## [0.5.0] - 2025-11-18

### Added - Stage 7: Admin Features
- **Admin Router** - Complete admin API endpoints
  - User management (list, update role, delete)
  - Artwork oversight (list, approve, delete)
  - System statistics
- **Authorization Guards** - Admin-only endpoint protection
- **Audit Logging** - Track admin actions for accountability
- **Admin Tests** - Integration tests for all admin endpoints

---

## [0.4.0] - 2025-11-17

### Added - Stage 6: Image Upload
- **Image Upload Endpoint** - File upload for artwork images
- **File Validation** - Type, size, and format validation
  - Allowed formats: JPG, PNG, WebP
  - Maximum size: 5MB
- **Image Storage** - File system storage with unique filenames
- **Upload Tests** - Integration tests for image upload functionality

---

## [0.3.0] - 2025-11-16

### Added - Stage 5: Statistics & Monitoring
- **Statistics API** - Comprehensive stats endpoints
  - Platform-wide statistics
  - Seller-specific statistics
  - User statistics
- **Health Endpoints** - Application and database health checks
- **Monitoring Integration** - Sentry error tracking setup
- **Stats Tests** - Integration tests for statistics endpoints

---

## [0.2.0] - 2025-11-15

### Added - Stage 4: Auction Logic
- **Auction Expiration** - Time-based auction closure
  - `end_date` field on artworks
  - Automatic status updates when auctions expire
  - Prevent bids on expired auctions
- **Auction Service** - Business logic for auction lifecycle
- **Bid Validation** - Enhanced validation for auction rules
- **Auction Tests** - Unit and integration tests for auction logic

### Added - Stage 3: Audit Logging
- **Audit Log Model** - SQLAlchemy model for audit trail
- **Logging Middleware** - Automatic logging of security events
  - User actions (login, register, profile updates)
  - Resource changes (artwork creation, bid placement)
  - Admin actions
- **Audit Endpoints** - Admin endpoints to view audit logs
- **Audit Tests** - Integration tests for audit logging

---

## [0.1.0] - 2025-11-14

### Added - Stage 2: Database Security
- **Database Indexes** - Indexes on `seller_id`, `artwork_id`, `bidder_id`, `auth0_sub`
- **Migration System** - Alembic migrations with rollback capability
- **Migration Tests** - Automated tests for migrations (upgrade/downgrade)
- **Database Constraints** - Foreign key constraints and unique constraints

### Added - Stage 1: Authentication & Authorization Fixes
- **JWT Token Validation** - Proper token verification in all endpoints
- **User Context Injection** - `get_current_user` dependency for protected routes
- **Authorization Guards** - Role-based access control (ADMIN, SELLER, BUYER)
- **Auth Service** - Centralized authentication logic
- **WebSocket Authentication** - JWT validation for WebSocket connections
- **Auth Tests** - Comprehensive integration tests for auth fixes

### Fixed
- **Critical Security Issues** - Fixed ID-based authorization bypass
  - Artworks: `seller_id` now extracted from JWT token
  - Bids: `bidder_id` now extracted from JWT token
  - Auth: `auth0_sub` now extracted from Bearer token
- **WebSocket Security** - Added authentication to WebSocket connections

---

## [0.0.1] - 2025-11-13

### Added - Stage 0: Initial Security Fixes
- **Environment Variables** - Moved all secrets to `.env` files
  - Auth0 credentials
  - JWT secret key
  - Database URL
  - Sentry DSN
- **Settings Module** - Centralized configuration with validation
- **Environment Templates** - `.env.example` files for backend and frontend
- **Security Documentation** - Initial SECURITY.md with known vulnerabilities

### Initial Project Setup
- **Backend** - FastAPI application structure
  - User, Artwork, Bid models
  - Basic CRUD endpoints
  - Auth0 integration
  - PostgreSQL database
- **Frontend** - React application structure
  - React 19 with Vite
  - Chakra UI components
  - Zustand state management
  - Auth0 authentication
- **DevOps** - Docker containerization
  - Docker Compose for local development
  - Backend and frontend Dockerfiles
  - PostgreSQL container

---

## Version History Summary

- **0.9.0** - Test infrastructure complete, 380 tests passing, comprehensive CI/CD
- **0.8.0** - Real-time bidding with WebSockets
- **0.7.0** - Performance optimization (eager loading, indexes)
- **0.6.0** - Pagination and rate limiting
- **0.5.0** - Admin features and audit logging
- **0.4.0** - Auction logic and image upload
- **0.3.0** - Statistics and monitoring
- **0.2.0** - Database security and migrations
- **0.1.0** - Authentication and authorization fixes
- **0.0.1** - Initial setup and environment security

---

## Pending Features

### High Priority
- **Stripe Payment Integration** - Payment flow implementation
  - Payment models and endpoints
  - Checkout component
  - Webhook handling
  - Payment tests

### Medium Priority
- **Database Seeding System** - Development and demo data
  - Seed scripts for users, artworks, bids
  - Test data generation utilities
  - Production-safe seeding

### Low Priority
- **Email Notifications** - Bid updates, auction results
- **Advanced Search** - Filter and sort artworks
- **User Profiles** - Enhanced user pages with history
- **Analytics Dashboard** - Advanced platform analytics

---

## Known Issues

See [SECURITY.md](SECURITY.md) for comprehensive list of security vulnerabilities.

### Critical Security Issues
- 3 Critical severity vulnerabilities
- 3 High severity vulnerabilities
- 4 Medium severity vulnerabilities

**DO NOT DEPLOY TO PRODUCTION** until security issues are resolved.

---

## Breaking Changes

### 0.1.0
- **API Authorization Changes** - All endpoints now require JWT tokens
  - Remove `seller_id` and `bidder_id` from request bodies
  - User identity is now extracted from Bearer token
  - Update API clients to use Bearer authentication

### 0.0.1
- **Environment Configuration Required** - Application will not start without `.env` files
  - Copy `.env.example` to `.env` in both backend and frontend
  - Configure all required variables

---

## Migration Guide

### From Development to 0.9.0

1. **Update Dependencies**
   ```bash
   # Backend
   cd backend
   pip install -r requirements.txt --upgrade

   # Frontend
   cd frontend
   npm install
   ```

2. **Run Migrations**
   ```bash
   cd backend
   alembic upgrade head
   ```

3. **Update Environment Files**
   - Check `.env.example` for new variables
   - Add any missing variables to your `.env`

4. **Run Tests**
   ```bash
   # Backend
   cd backend
   pytest --cov

   # Frontend
   cd frontend
   npm test -- --coverage
   ```

---

## Contributors

This project is developed as part of a DevOps course at DTU (Technical University of Denmark).

### Core Team
- Development team members (see git history for detailed contributions)

### Special Thanks
- DTU course instructors and advisors
- All contributors who helped improve the project

---

## Links

- **Repository:** https://github.com/MortenBeck/guess-the-worth
- **Issues:** https://github.com/MortenBeck/guess-the-worth/issues
- **Security Policy:** [SECURITY.md](SECURITY.md)
- **Contributing Guidelines:** [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Last Updated:** 2025-11-24
