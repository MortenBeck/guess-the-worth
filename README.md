# Guess The Worth

A full-stack web application for an artist collective featuring an innovative "bid what you want" auction system with hidden price thresholds. Built as a DevOps course project at DTU, demonstrating modern cloud deployment, CI/CD practices, and comprehensive testing strategies.

---

## 📊 Service Status

[![Backend Health](https://img.shields.io/uptimerobot/status/m801805858?label=Backend%20Health)](https://dashboard.uptimerobot.com/monitors/801805858)
[![Database](https://img.shields.io/uptimerobot/status/m801805868?label=Database)](https://dashboard.uptimerobot.com/monitors/801805868)
[![Frontend](https://img.shields.io/uptimerobot/status/m801805871?label=Frontend)](https://dashboard.uptimerobot.com/monitors/801805871)

**Local Monitoring**: [health-dashboard.html](health-dashboard.html) provides real-time service monitoring.

---

## 🎯 About

This project implements a unique auction platform where artworks have secret price thresholds unknown to bidders. The platform was developed with a strong focus on DevOps practices, including automated testing, continuous integration/deployment, cloud infrastructure, security scanning, and comprehensive monitoring.

**Course**: 62582 Complex Systems and Devops - Technical University of Denmark (DTU)

---

## 🏗️ Tech Stack

**Backend**: FastAPI, PostgreSQL, SQLAlchemy, Alembic, Socket.IO, Auth0, JWT, Sentry
**Frontend**: React 19, Vite, Zustand, TanStack Query, Chakra UI, React Router, Socket.io-client
**DevOps**: Docker, GitHub Actions, Azure App Services, UptimeRobot
**Testing**: Pytest, Vitest, Coverage.py, Jest
**Security**: TruffleHog, Trivy, Bandit, npm audit

---

## ✨ Key Features

### Core Functionality
- **Secret Threshold Bidding** - Artworks have hidden minimum prices; bidders guess their worth
- **Real-time Bidding** - WebSocket integration for instant bid updates across all clients
- **Stripe Payment Integration** - Complete PCI-compliant payment flow in demo mode
- **Role-Based Access Control** - Distinct permissions for Buyers, Sellers, and Admins
- **Auction System** - Time-based auctions with automatic closure and status management
- **Image Management** - Upload, optimization, and validation for artwork images

### DevOps Highlights
- **Azure Cloud Deployment** - Containerized backend and static frontend on Azure App Services
- **Automated CI/CD Pipeline** - GitHub Actions workflows for testing, security scanning, and deployment
- **Comprehensive Testing** - 142 tests across backend and frontend with coverage reporting
- **Security Scanning** - Automated secret detection, vulnerability scanning, and dependency auditing
- **Health Monitoring** - UptimeRobot integration, custom health dashboard, and Sentry error tracking
- **Database Migrations** - Alembic-based migrations with rollback capabilities

### Additional Features
- **Admin Dashboard** - User management, artwork oversight, and platform statistics
- **Audit Logging** - Complete action tracking for security and compliance
- **Performance Optimization** - Database indexing, pagination, rate limiting, and eager loading

---

## 🚀 Quick Start

```bash
# Clone and start with Docker
git clone <repository-url>
cd guess-the-worth
docker-compose up

# Access services:
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Environment Setup

```bash
# Backend configuration
cp backend/.env.example backend/.env
# Edit backend/.env with Auth0, JWT secret, database URL, Stripe keys

# Frontend configuration
cp frontend/.env.example frontend/.env
# Edit frontend/.env with Auth0 credentials and API URL

# Generate JWT secret
openssl rand -hex 32
```

See `.env.example` files for all required environment variables.

### Running Without Docker

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

## 🏛️ Architecture

```
Browser → React Frontend (Zustand + TanStack Query)
            ↓
        FastAPI Backend (Socket.IO)
            ↓
    PostgreSQL | Auth0 | Stripe API
```

**Database Schema**: Users, Artworks, Bids, Payments, AuditLogs

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

---

## 🧪 Testing & Quality Assurance

Testing is a core focus of this DevOps project, with comprehensive coverage across all layers:

**Test Suite**: 142 total tests
- Backend: 50 tests (unit, integration, e2e)
- Frontend: 92 tests (unit tests for stores and components)

**Coverage**:
- Backend: 65% coverage
- Frontend: 100% (state management stores)

**Running Tests**:
```bash
# Backend tests with coverage
cd backend && pytest --cov

# Frontend tests with coverage
cd frontend && npm test -- --coverage
```

---

## 🔄 CI/CD & DevOps Pipeline

Automated GitHub Actions workflows handle all aspects of continuous integration and deployment:

**Continuous Integration**:
- Automated testing on all pull requests
- Code coverage reporting
- Linting and formatting checks (Black, isort, Flake8)

**Security Scanning**:
- Secret detection with TruffleHog
- Container vulnerability scanning with Trivy
- Python security auditing with Bandit
- npm dependency vulnerability checks

**Continuous Deployment**:
- Automated deployment to Azure App Services on merge to main
- Containerized backend deployment
- Static frontend deployment
- Database migration automation

**Monitoring & Observability**:
- UptimeRobot monitoring for all services
- Sentry integration for error tracking
- Custom health dashboard for real-time status
- Comprehensive audit logging

---

## 🔒 Security

- **Authentication**: JWT tokens with Auth0 integration
- **Authorization**: Role-based access control (RBAC) for Admin, Seller, and Buyer roles
- **Rate Limiting**: Protection on critical endpoints to prevent abuse
- **Security Headers**: CSP, XSS protection, HSTS
- **Input Validation**: Pydantic (backend) and Zod (frontend) schemas
- **Audit Trail**: Complete logging of security-relevant actions
- **Secret Management**: All credentials in environment variables
- **Vulnerability Scanning**: Automated scanning in CI/CD pipeline

See [SECURITY.md](SECURITY.md) for complete security policy.

---

## 🚀 Deployment

**Production Infrastructure**:
- **Backend**: Azure App Service (Docker containerized)
- **Frontend**: Azure App Service (static hosting)
- **Database**: PostgreSQL (Azure managed service)

**Health Endpoints**:
- `GET /health` - Application health
- `GET /health/db` - Database connectivity
- `GET /api/admin/system/health` - Detailed system status (admin only)

**Monitoring**: UptimeRobot monitors all services with 5-minute intervals. View status badges above or check [health-dashboard.html](health-dashboard.html).

---

## 📚 Documentation

- [CONTRIBUTING.md](CONTRIBUTING.md) - Development workflow and contribution guidelines
- [CHANGELOG.md](CHANGELOG.md) - Complete project history and release notes
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture and design decisions
- [SECURITY.md](SECURITY.md) - Security policy and vulnerability reporting

---

## 🐛 Known Issues & Limitations

As a course project with defined scope and timeline, the following items remain:

**Frontend**:
- Artwork editing functionality not implemented for sellers
- Artwork image upload needs troubleshooting in production
- Platform activity dashboard uses mock data rather than real analytics
- Intermittent fetch errors on Azure-deployed frontend

**Backend**:
- Sentry frontend integration requires configuration
- Production database connection occasionally unstable

These issues reflect learning opportunities and areas for future enhancement rather than critical failures.

---

## 🛠️ Development Tools

This project utilized modern development tools to streamline implementation:

**Branch Strategy**: `main` (production) → `dev` (development) → `feature/*`, `bugfix/*`

**Commit Convention**: Semantic commit messages (`feat:`, `fix:`, `test:`, `docs:`, `chore:`, `refactor:`, `perf:`)

**AI-Assisted Development**: [Claude Code](https://claude.com/claude-code) was used throughout the project for commit message generation and documentation writing, improving consistency and development velocity.

---

**Last Updated**: 2025-12-03
