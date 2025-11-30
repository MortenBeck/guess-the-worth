# Guess The Worth

A web application for an artist collective selling paintings through an innovative "bid what you want" system with secret price thresholds.

**Status**: 🚧 In Development | DevOps Course Project - DTU

---

## 📊 Service Status

[![Backend Health](https://img.shields.io/uptimerobot/status/m801805858?label=Backend%20Health)](https://dashboard.uptimerobot.com/monitors/801805858)
[![Database](https://img.shields.io/uptimerobot/status/m801805868?label=Database)](https://dashboard.uptimerobot.com/monitors/801805868)
[![Frontend](https://img.shields.io/uptimerobot/status/m801805871?label=Frontend)](https://dashboard.uptimerobot.com/monitors/801805871)

**Local Health Dashboard**: Open [health-dashboard.html](health-dashboard.html) for real-time service monitoring.

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

Copy example files and configure:

```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env with Auth0 credentials, JWT secret, database URL

# Frontend
cp frontend/.env.example frontend/.env
# Edit frontend/.env with Auth0 credentials, API URL
```

**Generate JWT Secret**: `openssl rand -hex 32`

See `.env.example` files for all required variables.

### Database Seeding

Populate the database with demo data for testing and demonstration:

**Local/Docker:**

```bash
# Local
cd backend
python seeds/seed_manager.py

# Docker
docker exec guess_the_worth_backend python seeds/seed_manager.py
```

**Azure Production:**

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to your Backend App Service
3. In the left menu, go to **Development Tools** → **SSH** or **Console**
4. Run the seeding command:
   ```bash
   cd /home/site/wwwroot
   python seeds/seed_manager.py --env production
   ```
5. Type `yes` when prompted to confirm production seeding

**Demo Accounts** (for Auth0 testing - create these users in your Auth0 tenant):

| Role   | Email                      | Name                        | auth0_sub              |
| ------ | -------------------------- | --------------------------- | ---------------------- |
| Admin  | admin@guesstheworth.demo   | Demo Admin                  | auth0\|demo-admin-001  |
| Seller | seller1@guesstheworth.demo | Alice Johnson (Demo Seller) | auth0\|demo-seller-001 |
| Seller | seller2@guesstheworth.demo | Bob Martinez (Demo Seller)  | auth0\|demo-seller-002 |
| Seller | seller3@guesstheworth.demo | Carol Chen (Demo Seller)    | auth0\|demo-seller-003 |
| Buyer  | buyer1@guesstheworth.demo  | David Smith (Demo Buyer)    | auth0\|demo-buyer-001  |
| Buyer  | buyer2@guesstheworth.demo  | Emma Wilson (Demo Buyer)    | auth0\|demo-buyer-002  |
| Buyer  | buyer3@guesstheworth.demo  | Frank Brown (Demo Buyer)    | auth0\|demo-buyer-003  |
| Buyer  | buyer4@guesstheworth.demo  | Grace Lee (Demo Buyer)      | auth0\|demo-buyer-004  |
| Buyer  | buyer5@guesstheworth.demo  | Henry Taylor (Demo Buyer)   | auth0\|demo-buyer-005  |

**Seeded Content:**

- 15 artworks across various categories (Landscape, Abstract, Portrait, etc.)
- Multiple bid histories showing realistic auction activity
- Mix of ACTIVE, SOLD, and ARCHIVED artwork statuses
- Artworks with different auction end dates for testing

**Note**: The seeding system is idempotent - safe to run multiple times without duplicating data.

---

## 📊 Implementation Status

### ✅ Completed

- **Backend Security** - All secrets in environment variables with validation
- **Database Migrations** - Alembic migrations with rollback tests
- **Authentication System** - JWT + Auth0 with role-based access control
- **API Endpoints** - Complete REST API for artworks, bids, users, admin
- **Frontend Application** - React 19 with routing, state management, UI components
- **WebSocket Integration** - Real-time bidding updates via Socket.IO
- **Testing Suite** - 142 tests (backend: 50/51, frontend: 92/92)
- **CI/CD Pipeline** - GitHub Actions workflows for testing, security, deployment
- **Performance Optimization** - Database indexes, pagination, rate limiting, eager loading
- **Monitoring** - Health endpoints, Sentry integration, audit logging, custom health dashboard, UptimeRobot monitoring
- **Image Upload** - File validation, optimization, and storage
- **Admin Dashboard** - User management, artwork oversight
- **Security** - Rate limiting, security headers, input validation, RBAC
- **Documentation** - Complete project documentation (CONTRIBUTING.md, CHANGELOG.md, ARCHITECTURE.md)
- **Database Seeding System** - Idempotent seed scripts for users, artworks, and bids

### ❌ Pending Implementation

- **Stripe Payment Integration** - Infrastructure ready, payment flow needs implementation

---

## 🏗️ Tech Stack

**Backend**: FastAPI, PostgreSQL, SQLAlchemy, Alembic, Socket.IO, Auth0, JWT, Sentry
**Frontend**: React 19, Vite, Zustand, TanStack Query, Chakra UI, React Router, Socket.io-client
**DevOps**: Docker, GitHub Actions, Azure App Services, Pytest, Vitest

---

## 🏛️ Architecture

```
Browser → Frontend (React + Zustand) → Backend (FastAPI + Socket.IO) → PostgreSQL | Auth0 | Stripe
```

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

### Database Schema

**Users**: id, auth0_sub, email, name, role (buyer/seller/admin), timestamps
**Artworks**: id, title, description, artist_name, seller_id, image_url, secret_threshold, current_highest_bid, status, category, end_date
**Bids**: id, artwork_id, buyer_id, amount, status, timestamp
**Payments**: Not yet implemented
**AuditLogs**: id, user_id, action, resource_type, resource_id, ip_address, user_agent, timestamp

---

## 🧪 Testing

**Backend**: `cd backend && pytest --cov`
**Frontend**: `cd frontend && npm test -- --coverage`

**Coverage**: Backend 65% | Frontend 100% (stores)
**Tests**: 142 total (50 backend unit/integration/e2e, 92 frontend unit)

---

## 🚀 Deployment

**CI/CD**: Automated via GitHub Actions
**Backend**: Azure App Service (containerized)
**Frontend**: Azure App Service (static)
**Database**: PostgreSQL (Azure or managed service)

**Health Monitoring**:

- `/health` - Application health
- `/health/db` - Database connectivity
- `/api/admin/system/health` - System status (admin only)
- [health-dashboard.html](health-dashboard.html) - Real-time service monitoring dashboard

---

## 🔒 Security

- JWT + Auth0 authentication
- Role-based access control (ADMIN, SELLER, BUYER)
- Rate limiting on critical endpoints
- Security headers (CSP, XSS protection)
- Input validation (Pydantic backend, Zod frontend)
- Audit logging for security events
- Sentry error tracking
- Secret scanning (TruffleHog) in CI/CD
- Vulnerability scanning (Trivy, Bandit, npm audit)

See [SECURITY.md](SECURITY.md) for security policy.

---

## 📝 Development

**Branch Strategy**: `main` (production) → `dev` (development) → `feature/*`, `bugfix/*`

**Commit Convention**: `feat:`, `fix:`, `test:`, `docs:`, `chore:`, `refactor:`, `perf:`

**Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed development guidelines.

**Running Locally**:

```bash
# Backend
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn main:socket_app --reload

# Frontend
cd frontend
npm install
npm run dev
```

---

## 📚 Key Features

- **Secret Threshold Bidding** - Artworks have hidden price thresholds
- **Real-time Updates** - WebSocket bidding updates
- **Role-Based Access** - Buyer, Seller, Admin roles
- **Image Management** - Upload, optimize, validate artwork images
- **Auction System** - Time-based auctions with automatic closure
- **Admin Tools** - User management, artwork oversight
- **Statistics** - User, seller, and platform-wide stats
- **Audit Trail** - Complete action logging

---

## 🎯 Next Steps

1. **Implement Stripe Payment Flow**
   - Payment models and endpoints
   - Checkout component
   - Webhook handling

2. **Fix SENTRY Frontend**

3. **Fix Possible issue with db in production**

- "Failed to fetch (gtw-hgdyfdfdd2bjducu.swedencentral-01.azurewebsites.net)" on artworks page

---

## 📚 Documentation

- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contribution guidelines and development workflow
- **[CHANGELOG.md](CHANGELOG.md)** - Complete project history and release notes
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Detailed technical architecture documentation
- **[SECURITY.md](SECURITY.md)** - Security policy and known vulnerabilities

---

**Last Updated**: 2025-11-25
