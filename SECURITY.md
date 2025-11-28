# Security Policy

## Supported Versions

We take security seriously and strive to keep our application secure. The following versions are currently supported with security updates:

| Version           | Supported          |
| ----------------- | ------------------ |
| Latest (main)     | :white_check_mark: |
| Development (dev) | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly. We appreciate your efforts to help keep our project secure.

### How to Report

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report security vulnerabilities by:

1. **GitHub Security Advisories** (Preferred)
   - Go to the [Security tab](../../security/advisories) of this repository
   - Click "Report a vulnerability"
   - Fill out the form with details

2. **Email** (Alternative)
   - Contact the maintainers directly (check repository settings for contact info)
   - Include detailed information about the vulnerability

### What to Include

Please include the following information in your report:

- **Description**: A clear description of the vulnerability
- **Impact**: What could an attacker accomplish?
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Affected Components**: Which part of the application is affected (frontend, backend, etc.)
- **Suggested Fix**: If you have one, please share your thoughts
- **CVE Information**: If applicable, reference any related CVEs

### What to Expect

- **Acknowledgment**: We'll acknowledge receipt of your report within 48 hours
- **Updates**: We'll keep you informed about our progress
- **Timeline**: We aim to release fixes for critical vulnerabilities within 7 days
- **Credit**: If you wish, we'll publicly credit you for the discovery once the issue is resolved

## Security Measures

This project implements several security measures:

- **Automated Scanning**:
  - Trivy container vulnerability scanning (MEDIUM+ severity enforcement)
  - Dependabot dependency alerts
  - npm audit / pip-audit for dependency vulnerabilities
  - Bandit static analysis for Python code
  - TruffleHog secret scanning

- **CI/CD Security**:
  - Automated security checks on all PRs
  - Code quality and linting enforcement
  - Test coverage monitoring

- **Container Security**:
  - Distroless base images (minimal attack surface)
  - Multi-stage builds (no build tools in production)
  - Regular base image updates

## Known Security Issues

> **⚠️ IMPORTANT**: This application is currently in active development and contains **CRITICAL security vulnerabilities** that must be addressed before production deployment.

The following security issues have been identified through comprehensive security analysis (January 2025):

### 🔴 CRITICAL Severity

#### 1. Hardcoded Auth0 Credentials

- **File**: `backend/config/settings.py` (lines 18-20)
- **Issue**: `auth0_client_secret` and other sensitive credentials are hardcoded in source code
- **Risk**: Anyone with repository access can compromise the Auth0 tenant
- **Status**: ❌ **UNFIXED**
- **Remediation**: Stage 0 of [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Move all secrets to environment variables
- **CVSSv3**: 9.8 (Critical)

#### 2. ID-Based Authorization Bypass

- **Files**: `backend/routers/artworks.py:30`, `backend/routers/bids.py:20`
- **Issue**: `seller_id` and `bidder_id` are passed as query parameters instead of extracted from authenticated tokens
- **Exploit**: Any user can create artworks or place bids as any other user by manipulating query parameters
  ```bash
  # Example exploit:
  POST /api/bids/?bidder_id=999  # Impersonate user 999
  ```
- **Risk**: Complete authentication bypass, data integrity compromise
- **Status**: ❌ **UNFIXED**
- **Remediation**: Stage 1 of [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Extract user IDs from JWT tokens
- **CVSSv3**: 9.1 (Critical)

#### 3. Insecure User Lookup Endpoint

- **File**: `backend/routers/auth.py:37-42`
- **Issue**: `GET /api/auth/me?auth0_sub=<value>` allows looking up any user by providing their auth0_sub as a query parameter
- **Risk**: User enumeration, privacy violation, information disclosure
- **Status**: ❌ **UNFIXED**
- **Remediation**: Stage 1 of [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Extract auth0_sub from Bearer token
- **CVSSv3**: 7.5 (High)

### 🟠 HIGH Severity

#### 4. Unauthenticated WebSocket Connections

- **File**: `backend/main.py:55-76`
- **Issue**: WebSocket connections do not validate authentication tokens
- **Risk**: Unauthorized access to real-time bid data, potential for fake event injection
- **Status**: ❌ **UNFIXED**
- **Remediation**: Stage 1 of [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Validate JWT tokens in WebSocket connect handler
- **CVSSv3**: 7.5 (High)

#### 5. Missing Real-Time Bid Events

- **File**: `backend/routers/bids.py:65-67`
- **Issue**: Socket.IO event emission is commented out, but endpoint is still vulnerable to abuse
- **Risk**: While feature is disabled, the infrastructure is still exposed without proper authentication
- **Status**: ❌ **UNFIXED**
- **Remediation**: Stage 1 (authentication) + Stage 7 (implementation) of [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
- **CVSSv3**: 6.5 (Medium-High)

#### 6. No Auction Expiration Logic

- **File**: `backend/models/artwork.py`
- **Issue**: Missing `end_date` field and expiration logic - auctions never automatically end
- **Risk**: Business logic vulnerability, indefinite exposure of auction data
- **Status**: ❌ **UNFIXED**
- **Remediation**: Stage 2 (database) + Stage 4 (logic) of [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)
- **CVSSv3**: 5.3 (Medium)

### 🟡 MEDIUM Severity

#### 7. Missing Database Indexes

- **Files**: `backend/models/artwork.py`, `backend/models/bid.py`
- **Issue**: Foreign keys (`seller_id`, `artwork_id`, `bidder_id`) are not indexed
- **Risk**: Performance degradation enabling potential DoS through slow queries
- **Status**: ❌ **UNFIXED**
- **Remediation**: Stage 2 of [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)

#### 8. N+1 Query Vulnerabilities

- **Files**: `backend/routers/bids.py:15`, `backend/routers/artworks.py:14`
- **Issue**: Lazy loading of relationships causes N+1 queries
- **Risk**: Database performance issues, potential DoS vector
- **Status**: ❌ **UNFIXED**
- **Remediation**: Stage 9 of [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)

#### 9. No Pagination Limits

- **Files**: `backend/routers/artworks.py:14`, `backend/routers/users.py:18`
- **Issue**: No maximum limit enforced on pagination (client can request `?limit=999999`)
- **Risk**: Resource exhaustion, potential DoS
- **Status**: ❌ **UNFIXED**
- **Remediation**: Stage 8 of [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)

#### 10. Incomplete Image Upload Implementation

- **File**: `backend/routers/artworks.py:51-59`
- **Issue**: Image upload endpoint returns placeholder message only, no actual file handling
- **Risk**: If implemented incorrectly later, could lead to arbitrary file upload vulnerabilities
- **Status**: ❌ **NOT IMPLEMENTED**
- **Remediation**: Stage 6 of [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) - Implement with proper validation

### 📊 Application Security Issue Summary

| Severity    | Count  | Fixed | Unfixed |
| ----------- | ------ | ----- | ------- |
| 🔴 Critical | 3      | 3     | 0       |
| 🟠 High     | 3      | 3     | 0       |
| 🟡 Medium   | 4      | 4     | 0       |
| **TOTAL**   | **10** | **10** | **0**  |

**Status**: ✅ **ALL APPLICATION VULNERABILITIES RESOLVED** (as of v0.9.0 + Auth0 migration)

### 🔒 Dependency Security Status (Updated 2025-11-28)

| Package      | Version | Vulnerability | Severity | Status |
| ------------ | ------- | ------------- | -------- | ------ |
| flask-cors   | 6.0.1   | CVE-2024-6866, CVE-2024-6844, CVE-2024-6839 | HIGH | ✅ FIXED |
| jupyter-core | 5.9.1   | CVE-2025-30167 | MEDIUM | ✅ FIXED |
| jupyterlab   | 4.5.0   | CVE-2025-59842 | MEDIUM | ✅ FIXED |
| tornado      | 6.5.2   | CVE-2025-47287 | MEDIUM | ✅ FIXED |
| werkzeug     | 3.1.3   | CVE-2024-34069, CVE-2024-49766, CVE-2024-49767 | MEDIUM | ✅ FIXED |
| pip          | 25.3    | CVE-2025-8869 | MEDIUM | ✅ FIXED |
| setuptools   | 80.9.0  | CVE-2025-47273 | MEDIUM | ✅ FIXED |
| ecdsa        | 0.19.1  | CVE-2024-23342 | MEDIUM | ⚠️ NO FIX AVAILABLE |

**Dependency Summary**: 7 of 8 vulnerabilities patched. The remaining ecdsa timing attack vulnerability has no available fix and is considered out of scope by the package maintainers.

### ✅ Production Deployment Status

**READY FOR PRODUCTION** - All critical application vulnerabilities have been resolved:

- ✅ Stage 0 complete (environment security)
- ✅ Stage 1 complete (authentication & authorization fixes)
- ✅ Stage 2 complete (database security)
- ✅ All 10 implementation stages complete
- ✅ Dependency vulnerabilities patched (7/8)

**Note**: The remaining ecdsa vulnerability (CVE-2024-23342) is a timing attack that requires specific conditions and is generally considered acceptable risk for most applications.

---

## Security Best Practices

When contributing to this project, please:

- Never commit secrets, API keys, or credentials
- Keep dependencies up to date
- Follow secure coding practices
- Write tests for security-critical code
- Review security scan results before merging
- **Refer to [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md)** for secure implementation guidance

## Dependency Updates

We regularly update dependencies to address security vulnerabilities:

- **Dependabot**: Automatically creates PRs for vulnerable dependencies
- **Trivy**: Scans container images for known vulnerabilities
- **Manual Review**: Security updates are prioritized and reviewed promptly

## Questions?

If you have questions about security but don't have a vulnerability to report, feel free to open a regular GitHub issue or discussion.

Thank you for helping keep this project secure!
