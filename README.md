# Danish Artist Marketplace

A modern web application for a Danish artist collective selling paintings through an innovative "bid what you want" system with secret price thresholds. Built as a comprehensive DevOps course project demonstrating full-stack development, containerization, CI/CD, and modern deployment practices.

## Project Concept

Three Danish artists have formed a collective and want a unified web sales platform. Their innovative concept: **"Byd hvad du vil og hvis du rammer den hemmelige grænse - så ok"** (Bid what you want, and if you hit the secret threshold - then okay).

### How It Works
- Artists upload paintings with a secret minimum price
- Buyers place bids without knowing the threshold
- When a bid meets or exceeds the secret price, the sale is complete
- Real-time bidding creates an engaging, competitive experience

##  User Types

- **Buyers**: Browse artwork, place bids, track auction status
- **Sellers (Artists)**: Upload artwork, set secret thresholds, manage inventory
- **Admins**: Platform oversight, user management, transaction monitoring

##  Key Features

### Real-time Bidding System
- Live bid updates using WebSocket connections
- Per-artwork bidding rooms
- Automatic notifications when thresholds are met
- Rate limiting to prevent spam bidding

### Multi-User Authentication
- Social login via Auth0 (Google, Facebook, etc.)
- Role-based access control
- Secure JWT token management
- No password management required

### Secure Payment Processing
- Stripe integration for payment handling
- Marketplace functionality for multi-party transactions
- Test mode for development and demonstration
- Automatic fund distribution to artists

### Image Management
- Secure file upload with validation
- Image optimisation and thumbnail generation
- Cloud storage integration
- Gallery view with responsive design

## 🛠 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework with async support
- **PostgreSQL** - Relational database with advanced features
- **SQLAlchemy** - ORM for database operations
- **Socket.IO** - Real-time WebSocket communication
- **Auth0** - Social authentication and user management
- **Stripe** - Payment processing and marketplace features

### Frontend
- **React** - Component-based UI framework
- **Chakra UI** - Accessible component library
- **Zustand** - Lightweight state management
- **TanStack Query** - Server state management and caching
- **Vite** - Fast build tool and development server

### DevOps & Deployment
- **Docker** - Containerization for consistent deployments
- **GitHub Actions** - CI/CD pipeline automation
- **Render** - Cloud platform for hosting (free tier)
- **PostgreSQL** - Managed database hosting

### Testing
- **Pytest** - Backend API and WebSocket testing
- **Vitest** - Fast frontend testing framework
- **React Testing Library** - Component testing utilities

##  Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Git

### Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/MortenBeck/guess-the-worth
   cd guess-the-worth
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

### Manual Setup (Alternative)

**Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**Frontend Setup:**
```bash
cd frontend
npm install
npm run dev
```

**Database Setup:**
```bash
# Using Docker
docker run --name postgres-marketplace -e POSTGRES_PASSWORD=password -e POSTGRES_DB=marketplace -p 5432:5432 -d postgres:15

# Run migrations
cd backend
alembic upgrade head
```

##  Project Structure


## 🔧 API Documentation

### Authentication Endpoints
- `POST /auth/login` - Initiate social login
- `POST /auth/callback` - Handle Auth0 callback
- `POST /auth/logout` - User logout

### Artwork Management
- `GET /artworks` - List all artworks with pagination
- `POST /artworks` - Upload new artwork (sellers only)
- `GET /artworks/{id}` - Get artwork details
- `PUT /artworks/{id}` - Update artwork (owner only)
- `DELETE /artworks/{id}` - Remove artwork (owner/admin only)

### Bidding System
- `POST /artworks/{id}/bids` - Place a bid
- `GET /artworks/{id}/bids` - Get bidding history
- `WebSocket /ws/auctions/{id}` - Real-time bid updates

### User Management
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile
- `GET /users/{id}` - Get user public profile (artists only)

### Payment Processing
- `POST /payments/create-intent` - Create Stripe payment intent
- `POST /payments/webhook` - Stripe webhook handler
- `GET /payments/history` - User payment history

Interactive API documentation available at `/docs` when running the backend.

##  Testing

### Run Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

### Run Frontend Tests
```bash
cd frontend
npm run test
npm run test:coverage
```

### Integration Testing
```bash
# Start test environment
docker-compose -f docker-compose.test.yml up --build
```

##  Deployment

### Production Deployment on Render

1. **Deploy Backend**
   - Connect GitHub repository to Render
   - Configure environment variables
   - Deploy from `main` branch

2. **Deploy Frontend**
   - Build command: `npm run build`
   - Publish directory: `dist`
   - Configure API endpoint

3. **Database Setup**
   - Add PostgreSQL addon on Render
   - Run database migrations

### Environment Variables

**Backend (.env)**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/marketplace
AUTH0_DOMAIN=your-auth0-domain.auth0.com
AUTH0_API_AUDIENCE=your-api-identifier
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

**Frontend (.env)**
```env
VITE_API_URL=http://localhost:8000
VITE_AUTH0_DOMAIN=your-auth0-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_AUTH0_AUDIENCE=your-api-identifier
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

##  DevOps Features

### Continuous Integration
- Automated testing on all pull requests
- Code quality checks with ESLint and Black
- Security vulnerability scanning
- Docker image building and testing

### Continuous Deployment
- Automatic deployment from `main` branch
- Database migration automation
- Environment-specific configurations
- Rollback capabilities

### Monitoring
- Application performance monitoring
- Error tracking and alerting
- Database performance metrics
- User analytics and usage patterns

## 🎓 Course Learning Objectives

This project demonstrates:

- **Frontend/Backend Frameworks**: React with Chakra UI and FastAPI
- **Application State Management**: Zustand for client state, TanStack Query for server state
- **Backend Security**: JWT tokens, Auth0 integration, input validation
- **Package Management**: npm for frontend, pip for backend
- **CI/CD Implementation**: GitHub Actions with automated testing and deployment
- **Containerization**: Docker multi-stage builds, Docker Compose orchestration
- **DevOps Practices**: Infrastructure as code, automated deployments, monitoring

### Optional Real-time Features
- WebSocket implementation for live bidding
- Publish-subscribe architecture with Socket.IO
- Event-driven notifications and updates

##  Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code style (Black for Python, Prettier for JavaScript)
- Write tests for new features
- Update documentation as needed
- Ensure all CI checks pass

##  Development Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [x] Project setup and repository structure
- [x] Basic FastAPI backend with database models
- [x] React frontend with routing and authentication
- [x] Docker development environment

### Phase 2: Core Features (Weeks 3-4)
- [ ] Artwork upload and management system
- [ ] Basic bidding functionality
- [ ] User role management
- [ ] Stripe test integration

### Phase 3: Real-time Features (Weeks 5-6)
- [ ] WebSocket bidding implementation
- [ ] Live notifications and updates
- [ ] Advanced UI interactions
- [ ] Comprehensive testing suite

### Phase 4: Production Ready (Weeks 7-8)
- [ ] CI/CD pipeline optimisation
- [ ] Security hardening
- [ ] Performance monitoring
- [ ] Documentation completion

## Known Issues

- Cold start delays on Render free tier (~50 seconds)
- WebSocket connections may require reconnection on deployment
- File upload size limited to 5MB on free hosting

## Support

For questions about this educational project:
- Course discussion forum
- GitHub Issues for bug reports
- Project team collaboration channels

## License

This project is created for educational purposes as part of a DevOps course. Not intended for commercial use.

---

**Built with care for learning modern web development and DevOps practices**
