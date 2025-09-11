# Guess The Worth

A web application for an artist collective selling paintings through an innovative "bid what you want" system with secret price thresholds. Built as a comprehensive DevOps course project demonstrating full-stack development, containerization, CI/CD, and modern deployment practices.

## Project Concept

Three artists have formed a collective and want a unified web sales platform. Their innovative concept: "Bid what you want, and if you hit the secret threshold, then okay".

### How It Works
- Artists upload paintings with a secret minimum price
- Buyers place bids without knowing the threshold
- When a bid meets or exceeds the secret price, the sale is complete
- Real-time bidding creates an engaging, competitive experience

## User Types

- **Buyers**: Browse artwork, place bids, track auction status
- **Sellers (Artists)**: Upload artwork, set secret thresholds, manage inventory
- **Admins**: Platform oversight, user management, transaction monitoring

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework with async support
- **PostgreSQL** - SQL database with advanced features
- **SQLAlchemy** - Python ORM for database operations
- **Socket.IO** - Real-time WebSocket communication for live bidding
- **Auth0** - Social authentication and user management
- **Stripe** - Payment processing (test mode)
- **Aiofiles** - Async file handling for image uploads
- **Pillow** - Image processing and validation

### Frontend
- **React** - Component-based UI framework
- **Zustand** - Lightweight state management (in addition to useState)
- **TanStack Query** - Server state management and caching
- **Chakra UI** - Accessible component library
- **Socket.io-client** - WebSocket client for real-time bidding
- **React-dropzone** - File upload component
- **Auth0 React SDK** - Social authentication integration
- **Vite** - Build tool and development server

### DevOps & Deployment
- **Docker** - Containerization
- **GitHub Actions** - CI/CD pipeline for testing and deployment
- **Render** - Free tier cloud hosting platform
- **PostgreSQL** - Managed database hosting

### Testing
- **Pytest** - Backend testing framework
- **Vitest** - Fast frontend testing (4x faster than Jest)
- **React Testing Library** - Component testing utilities

### Key Features
- **Real-time bidding system** with WebSocket connections
- **Social authentication** (Google, Facebook, etc.) - no password management
- **Secure file upload** with image validation and processing
- **Payment processing** with Stripe marketplace functionality
- **Role-based access control** for buyers, sellers, and admins
- **Free deployment** on Render platform

## Course Learning Objectives

This project demonstrates:
- Frontend and backend development frameworks
- Application state management
- Backend security and token-based authentication
- Package management
- Continuous integration, test and delivery (CI/CD)
- Containerization and build servers
- DevOps practices
- Real-time web applications using publish-subscribe architecture

## Project Status

This is an educational project for a DevOps course. Implementation details and setup instructions will be added as development progresses.
