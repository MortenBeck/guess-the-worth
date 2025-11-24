# Architecture Documentation

This document provides a comprehensive overview of the Guess The Worth application architecture, including system design, technology stack, data flow, and key design decisions.

---

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagram](#architecture-diagram)
- [Technology Stack](#technology-stack)
- [Backend Architecture](#backend-architecture)
- [Frontend Architecture](#frontend-architecture)
- [Database Design](#database-design)
- [Authentication & Authorization](#authentication--authorization)
- [Real-time Communication](#real-time-communication)
- [API Design](#api-design)
- [Security Architecture](#security-architecture)
- [Infrastructure & DevOps](#infrastructure--devops)
- [Performance & Scalability](#performance--scalability)
- [Monitoring & Observability](#monitoring--observability)
- [Design Decisions & Trade-offs](#design-decisions--trade-offs)

---

## System Overview

Guess The Worth is a web-based auction platform for an artist collective, featuring a unique "bid what you want" system with secret price thresholds. The application follows a modern three-tier architecture:

1. **Presentation Layer** - React-based SPA with real-time updates
2. **Application Layer** - FastAPI REST API with WebSocket support
3. **Data Layer** - PostgreSQL relational database

### Key Features
- Secret threshold bidding system
- Real-time bid updates via WebSockets
- Role-based access control (Buyer, Seller, Admin)
- Image upload and management
- Time-based auction expiration
- Comprehensive admin dashboard
- Audit logging for security events

### Architecture Principles
- **Separation of Concerns** - Clear boundaries between layers
- **Stateless API** - JWT-based authentication, no server-side sessions
- **Real-time First** - WebSocket integration for live updates
- **Security by Design** - Authentication, authorization, rate limiting, audit logs
- **Testability** - High test coverage with comprehensive test suites
- **Scalability** - Containerized, horizontally scalable design

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Client Browser                            │
│                                                                     │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │  React 19       │  │  Zustand         │  │  Socket.io       │ │
│  │  (UI Layer)     │  │  (State Mgmt)    │  │  Client          │ │
│  └─────────────────┘  └──────────────────┘  └──────────────────┘ │
│           │                     │                      │           │
│           └─────────────────────┴──────────────────────┘           │
│                                 │                                  │
└─────────────────────────────────┼──────────────────────────────────┘
                                  │
                    ┌─────────────┴──────────────┐
                    │   HTTPS / WSS              │
                    │   (TLS Encrypted)          │
                    └─────────────┬──────────────┘
                                  │
┌─────────────────────────────────┼──────────────────────────────────┐
│                                 │                                  │
│                         Azure / Cloud                              │
│                                 │                                  │
│  ┌──────────────────────────────┴────────────────────────────┐   │
│  │              FastAPI Application Server                    │   │
│  │                                                             │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │   │
│  │  │ REST API     │  │ Socket.IO    │  │ Middleware      │ │   │
│  │  │ Endpoints    │  │ Server       │  │ (Rate Limit,    │ │   │
│  │  │              │  │              │  │  Security)      │ │   │
│  │  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘ │   │
│  │         │                  │                   │          │   │
│  │  ┌──────┴──────────────────┴───────────────────┴────────┐ │   │
│  │  │         Business Logic Layer                          │ │   │
│  │  │  (Services, Auth, Validation, Audit Logging)         │ │   │
│  │  └──────┬───────────────────────────────────────────────┘ │   │
│  │         │                                                  │   │
│  │  ┌──────┴────────────────────────────────────────────────┐│   │
│  │  │         Data Access Layer (SQLAlchemy ORM)            ││   │
│  │  └──────┬────────────────────────────────────────────────┘│   │
│  └─────────┼──────────────────────────────────────────────────┘   │
│            │                                                       │
│  ┌─────────┴──────────────────────────────────────────────┐      │
│  │              PostgreSQL Database                        │      │
│  │  ┌──────────────────────────────────────────────────┐  │      │
│  │  │  Tables: users, artworks, bids, audit_logs       │  │      │
│  │  │  Indexes, Foreign Keys, Constraints              │  │      │
│  │  └──────────────────────────────────────────────────┘  │      │
│  └─────────────────────────────────────────────────────────┘      │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘

External Services:
┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐
│  Auth0     │  │  Sentry    │  │ UptimeRobot│  │  Stripe    │
│  (Auth)    │  │  (Errors)  │  │ (Uptime)   │  │ (Payment)  │
└────────────┘  └────────────┘  └────────────┘  └────────────┘
```

---

## Technology Stack

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Primary backend language |
| FastAPI | Latest | High-performance web framework |
| SQLAlchemy | Latest | ORM for database interactions |
| Alembic | Latest | Database migration tool |
| Pydantic | Latest | Data validation and serialization |
| Socket.IO | Latest | WebSocket communication |
| Auth0 | N/A | Authentication provider |
| PyJWT | Latest | JWT token handling |
| Uvicorn | Latest | ASGI server |
| Pytest | Latest | Testing framework |
| Bandit | Latest | Security linting |
| Black | Latest | Code formatting |

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| React | 19 | UI library |
| Vite | Latest | Build tool and dev server |
| Zustand | Latest | State management |
| TanStack Query | Latest | Server state management |
| Chakra UI | Latest | Component library |
| React Router | Latest | Client-side routing |
| Socket.io-client | Latest | WebSocket client |
| Axios | Latest | HTTP client |
| Vitest | Latest | Testing framework |
| ESLint | Latest | Code linting |
| Prettier | Latest | Code formatting |

### Database
| Technology | Version | Purpose |
|------------|---------|---------|
| PostgreSQL | 15+ | Primary database |

### DevOps & Infrastructure
| Technology | Purpose |
|------------|---------|
| Docker | Containerization |
| Docker Compose | Local development orchestration |
| GitHub Actions | CI/CD pipeline |
| Azure App Services | Hosting (backend and frontend) |
| Sentry | Error tracking and monitoring |
| UptimeRobot | Uptime monitoring |
| Trivy | Container vulnerability scanning |
| TruffleHog | Secret scanning |

---

## Backend Architecture

### Layered Architecture

The backend follows a clean, layered architecture pattern:

```
┌─────────────────────────────────────────┐
│        Presentation Layer               │
│  (FastAPI Routers - HTTP/WebSocket)     │
└───────────────┬─────────────────────────┘
                │
┌───────────────┴─────────────────────────┐
│         Middleware Layer                │
│  (Auth, Rate Limiting, CORS, Security)  │
└───────────────┬─────────────────────────┘
                │
┌───────────────┴─────────────────────────┐
│       Business Logic Layer              │
│  (Services, Validation, Auth Logic)     │
└───────────────┬─────────────────────────┘
                │
┌───────────────┴─────────────────────────┐
│       Data Access Layer                 │
│  (SQLAlchemy Models, Database Session)  │
└───────────────┬─────────────────────────┘
                │
┌───────────────┴─────────────────────────┐
│          Database Layer                 │
│  (PostgreSQL)                           │
└─────────────────────────────────────────┘
```

### Directory Structure

```
backend/
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   └── env.py                  # Alembic configuration
├── config/
│   └── settings.py             # Application configuration
├── middleware/
│   ├── security_headers.py     # Security headers middleware
│   └── rate_limit.py           # Rate limiting middleware
├── models/                     # SQLAlchemy ORM models
│   ├── user.py
│   ├── artwork.py
│   ├── bid.py
│   └── audit_log.py
├── routers/                    # API endpoint routers
│   ├── auth.py                 # Authentication endpoints
│   ├── users.py                # User management
│   ├── artworks.py             # Artwork CRUD
│   ├── bids.py                 # Bidding endpoints
│   ├── admin.py                # Admin operations
│   ├── stats.py                # Statistics
│   └── health.py               # Health checks
├── schemas/                    # Pydantic schemas
│   ├── user.py
│   ├── artwork.py
│   └── bid.py
├── services/                   # Business logic
│   ├── auth_service.py         # Authentication logic
│   └── auction_service.py      # Auction business rules
├── tests/
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── e2e/                    # End-to-end tests
├── database.py                 # Database connection and session
├── main.py                     # Application entry point
└── requirements.txt            # Python dependencies
```

### Key Components

#### 1. Main Application ([main.py](backend/main.py))
- FastAPI app initialization
- Socket.IO server setup
- Middleware registration
- Router inclusion
- CORS configuration

#### 2. Database Layer ([database.py](backend/database.py))
- SQLAlchemy engine and session factory
- Connection pooling
- Session management with dependency injection

#### 3. Models
**Object-Relational Mapping (ORM) using SQLAlchemy**

- **User Model** - User accounts with Auth0 integration
- **Artwork Model** - Artwork listings with secret thresholds
- **Bid Model** - Bid records linked to users and artworks
- **AuditLog Model** - Security and action logging

#### 4. Routers
**RESTful API endpoints organized by resource**

Each router handles specific resource operations:
- Authentication and authorization
- CRUD operations
- Business logic invocation
- Response serialization

#### 5. Services
**Encapsulated business logic**

- **AuthService** - JWT validation, user context
- **AuctionService** - Auction lifecycle, expiration logic
- Separates business rules from HTTP layer

#### 6. Middleware
**Request/response interceptors**

- **Security Headers** - CSP, XSS protection, HSTS
- **Rate Limiting** - Sliding window rate limiter
- **CORS** - Cross-origin resource sharing
- **Error Handling** - Global exception handling

---

## Frontend Architecture

### Component-Based Architecture

The frontend follows a modern React architecture with functional components and hooks:

```
┌─────────────────────────────────────────┐
│           React Components              │
│  (Pages, Components, Layouts)           │
└───────────────┬─────────────────────────┘
                │
┌───────────────┴─────────────────────────┐
│        State Management Layer           │
│  (Zustand Stores, TanStack Query)       │
└───────────────┬─────────────────────────┘
                │
┌───────────────┴─────────────────────────┐
│         Service Layer                   │
│  (API Client, WebSocket Client)         │
└───────────────┬─────────────────────────┘
                │
┌───────────────┴─────────────────────────┐
│         Backend API                     │
│  (REST API, WebSocket)                  │
└─────────────────────────────────────────┘
```

### Directory Structure

```
frontend/
├── public/                     # Static assets
├── src/
│   ├── components/             # Reusable UI components
│   │   ├── ArtworkCard.jsx
│   │   ├── BidForm.jsx
│   │   ├── Header.jsx
│   │   └── ...
│   ├── pages/                  # Route-level pages
│   │   ├── HomePage.jsx
│   │   ├── ArtworkDetailPage.jsx
│   │   ├── AdminPage.jsx
│   │   └── ...
│   ├── store/                  # Zustand state stores
│   │   ├── authStore.js
│   │   ├── artworkStore.js
│   │   └── bidStore.js
│   ├── services/               # External service clients
│   │   ├── api.js              # REST API client
│   │   └── socket.js           # WebSocket client
│   ├── hooks/                  # Custom React hooks
│   │   ├── useAuth.js
│   │   ├── useWebSocket.js
│   │   └── ...
│   ├── utils/                  # Utility functions
│   ├── config/                 # Configuration
│   │   └── auth0.js
│   ├── theme/                  # Chakra UI theme
│   │   └── index.js
│   ├── test/                   # Test utilities
│   │   └── setup.js
│   ├── App.jsx                 # Main app component
│   └── main.jsx                # Entry point
├── vite.config.js              # Vite configuration
├── package.json
└── .env.example                # Environment template
```

### Key Patterns

#### 1. State Management
**Zustand for client state, TanStack Query for server state**

```javascript
// Zustand store example
const useAuthStore = create((set) => ({
  user: null,
  token: null,
  login: (user, token) => set({ user, token }),
  logout: () => set({ user: null, token: null })
}));
```

#### 2. Component Composition
**Small, focused components with clear responsibilities**

- **Pages** - Route-level components
- **Components** - Reusable UI elements
- **Layouts** - Common page structures

#### 3. Custom Hooks
**Encapsulate logic for reusability**

```javascript
// Custom hook example
const useAuth = () => {
  const { user, token, login, logout } = useAuthStore();
  const isAuthenticated = !!token;
  const isAdmin = user?.role === 'ADMIN';
  return { user, token, login, logout, isAuthenticated, isAdmin };
};
```

#### 4. API Client Pattern
**Centralized API communication with interceptors**

```javascript
// Axios client with auth interceptor
api.interceptors.request.use((config) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

---

## Database Design

### Entity-Relationship Diagram

```
┌──────────────────────┐         ┌──────────────────────┐
│       Users          │         │     Artworks         │
├──────────────────────┤         ├──────────────────────┤
│ id (PK)              │         │ id (PK)              │
│ auth0_sub (UNIQUE)   │◄───┐    │ title                │
│ email                │    │    │ description          │
│ name                 │    │    │ artist_name          │
│ role (ENUM)          │    │    │ seller_id (FK)       │────┐
│ created_at           │    │    │ image_url            │    │
│ updated_at           │    │    │ secret_threshold     │    │
└──────────────────────┘    │    │ current_highest_bid  │    │
         │                  │    │ status (ENUM)        │    │
         │                  └────┤ category             │    │
         │                       │ end_date             │    │
         │                       │ created_at           │    │
         │                       │ updated_at           │    │
         │                       └──────────────────────┘    │
         │                                │                  │
         │                                │                  │
         │                       ┌────────┴──────────┐       │
         │                       │                   │       │
         │                       ▼                   ▼       │
         │              ┌──────────────────────┐            │
         │              │        Bids          │            │
         │              ├──────────────────────┤            │
         │              │ id (PK)              │            │
         └──────────────┤ artwork_id (FK)      │            │
                        │ buyer_id (FK)        │────────────┘
                        │ amount               │
                        │ status (ENUM)        │
                        │ created_at           │
                        └──────────────────────┘
                                 │
                                 │
         ┌───────────────────────┘
         │
         ▼
┌──────────────────────┐
│    AuditLogs         │
├──────────────────────┤
│ id (PK)              │
│ user_id (FK)         │
│ action               │
│ resource_type        │
│ resource_id          │
│ ip_address           │
│ user_agent           │
│ timestamp            │
└──────────────────────┘
```

### Table Specifications

#### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    auth0_sub VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('ADMIN', 'SELLER', 'BUYER')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_auth0_sub ON users(auth0_sub);
CREATE INDEX idx_users_role ON users(role);
```

#### Artworks Table
```sql
CREATE TABLE artworks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    artist_name VARCHAR(255) NOT NULL,
    seller_id INTEGER NOT NULL REFERENCES users(id),
    image_url VARCHAR(500),
    secret_threshold DECIMAL(10, 2) NOT NULL,
    current_highest_bid DECIMAL(10, 2) DEFAULT 0,
    status VARCHAR(50) NOT NULL CHECK (status IN ('ACTIVE', 'SOLD', 'EXPIRED')),
    category VARCHAR(100),
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_artworks_seller_id ON artworks(seller_id);
CREATE INDEX idx_artworks_status ON artworks(status);
CREATE INDEX idx_artworks_category ON artworks(category);
CREATE INDEX idx_artworks_end_date ON artworks(end_date);
```

#### Bids Table
```sql
CREATE TABLE bids (
    id SERIAL PRIMARY KEY,
    artwork_id INTEGER NOT NULL REFERENCES artworks(id),
    buyer_id INTEGER NOT NULL REFERENCES users(id),
    amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('PENDING', 'WINNING', 'OUTBID', 'WON', 'LOST')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_bids_artwork_id ON bids(artwork_id);
CREATE INDEX idx_bids_buyer_id ON bids(buyer_id);
CREATE INDEX idx_bids_status ON bids(status);
```

#### AuditLogs Table
```sql
CREATE TABLE audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id INTEGER,
    ip_address VARCHAR(50),
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
```

### Database Relationships

- **One-to-Many**: User → Artworks (seller)
- **One-to-Many**: User → Bids (buyer)
- **One-to-Many**: Artwork → Bids
- **One-to-Many**: User → AuditLogs

### Indexing Strategy

**Indexed Fields:**
- Primary keys (automatic)
- Foreign keys (seller_id, buyer_id, artwork_id)
- Frequently queried fields (auth0_sub, status, category, end_date)
- Fields used in WHERE clauses and JOINs

**Rationale:**
- Improves query performance
- Prevents N+1 query issues
- Enables efficient pagination
- Supports real-time lookups

---

## Authentication & Authorization

### Authentication Flow

```
┌─────────────┐                ┌─────────────┐                ┌─────────────┐
│   Client    │                │   Auth0     │                │   Backend   │
└──────┬──────┘                └──────┬──────┘                └──────┬──────┘
       │                              │                              │
       │  1. Login Request            │                              │
       ├──────────────────────────────►                              │
       │                              │                              │
       │  2. Auth0 Hosted Login       │                              │
       ◄──────────────────────────────┤                              │
       │                              │                              │
       │  3. User Credentials         │                              │
       ├──────────────────────────────►                              │
       │                              │                              │
       │  4. ID Token + Access Token  │                              │
       ◄──────────────────────────────┤                              │
       │                              │                              │
       │  5. API Request with Bearer Token                           │
       ├─────────────────────────────────────────────────────────────►
       │                              │                              │
       │                              │  6. Validate Token           │
       │                              ◄──────────────────────────────┤
       │                              │                              │
       │                              │  7. Token Valid              │
       │                              ├──────────────────────────────►
       │                              │                              │
       │  8. Protected Resource       │                              │
       ◄─────────────────────────────────────────────────────────────┤
       │                              │                              │
```

### Authentication Implementation

#### Backend Token Validation

```python
# Extract and validate JWT token
async def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Extract user from JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.split(" ")[1]

    # Validate JWT with Auth0 public key
    payload = jwt.decode(
        token,
        auth0_public_key,
        algorithms=["RS256"],
        audience=settings.auth0_audience
    )

    # Lookup user in database
    auth0_sub = payload.get("sub")
    user = db.query(User).filter(User.auth0_sub == auth0_sub).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user
```

### Authorization (RBAC)

**Role Hierarchy:**
1. **ADMIN** - Full system access
2. **SELLER** - Create/manage artworks
3. **BUYER** - Place bids, view artworks

**Permission Guards:**

```python
# Role-based authorization decorator
def require_role(required_role: str):
    def decorator(func):
        async def wrapper(*args, current_user: User = Depends(get_current_user), **kwargs):
            if current_user.role != required_role:
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return await func(*args, current_user=current_user, **kwargs)
        return wrapper
    return decorator

# Usage
@router.get("/admin/users")
@require_role("ADMIN")
async def list_users(current_user: User = Depends(get_current_user)):
    # Only admins can access
    pass
```

### Security Considerations

- **Token Storage** - Stored in memory (Zustand), not localStorage
- **Token Refresh** - Automatic refresh before expiration
- **HTTPS Only** - All communication over TLS
- **Short-lived Tokens** - 1-hour expiration
- **Secure Cookies** - HttpOnly, Secure, SameSite attributes

---

## Real-time Communication

### WebSocket Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Socket.IO Flow                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Client 1                      Server                  Client 2  │
│     │                            │                        │       │
│     │  1. Connect (WSS)          │                        │       │
│     ├────────────────────────────►                        │       │
│     │                            │                        │       │
│     │  2. Join Room              │                        │       │
│     │     (artwork_<id>)         │                        │       │
│     ├────────────────────────────►                        │       │
│     │                            │                        │       │
│     │  3. Place Bid (HTTP)       │                        │       │
│     ├────────────────────────────►                        │       │
│     │                            │                        │       │
│     │                            │  4. Broadcast Event    │       │
│     │                            │      (new_bid)         │       │
│     │                            ├────────────────────────┼──────►│
│     ◄────────────────────────────┤                        │       │
│     │                            │                        │       │
│     │  5. UI Update              │  6. UI Update          │       │
│     │     (real-time)            │     (real-time)        │       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### Implementation

#### Server-Side (Backend)

```python
# Socket.IO server setup in main.py
socket_app = SocketIOApp(
    app,
    socketio_path="socket.io",
    cors_allowed_origins=["http://localhost:5173"]
)

@socket_app.on("connect")
async def handle_connect(sid, environ):
    """Handle WebSocket connection."""
    # TODO: Validate JWT token from connection
    print(f"Client {sid} connected")

@socket_app.on("join_artwork")
async def handle_join_artwork(sid, data):
    """Client joins artwork room for updates."""
    artwork_id = data.get("artwork_id")
    await socket_app.enter_room(sid, f"artwork_{artwork_id}")

# Emit event when bid is placed
await socket_app.emit(
    "new_bid",
    {"artwork_id": bid.artwork_id, "amount": bid.amount},
    room=f"artwork_{artwork_id}"
)
```

#### Client-Side (Frontend)

```javascript
// WebSocket client in services/socket.js
import io from 'socket.io-client';

const socket = io(API_URL, {
  transports: ['websocket'],
  auth: {
    token: getAuthToken() // TODO: Send JWT token
  }
});

// Join artwork room
socket.emit('join_artwork', { artwork_id: artworkId });

// Listen for bid updates
socket.on('new_bid', (data) => {
  // Update UI with new bid
  updateArtworkStore(data);
});
```

### Event Types

| Event | Direction | Purpose |
|-------|-----------|---------|
| `connect` | Client → Server | Establish WebSocket connection |
| `disconnect` | Client → Server | Close WebSocket connection |
| `join_artwork` | Client → Server | Subscribe to artwork updates |
| `leave_artwork` | Client → Server | Unsubscribe from artwork |
| `new_bid` | Server → Client | Broadcast new bid to all clients |
| `auction_ended` | Server → Client | Notify auction expiration |

---

## API Design

### RESTful Principles

The API follows REST architectural constraints:

- **Resource-Based URLs** - `/api/artworks`, `/api/bids`
- **HTTP Verbs** - GET, POST, PUT, DELETE
- **Stateless** - Each request contains all necessary information
- **JSON Format** - Request and response bodies use JSON
- **HTTP Status Codes** - Semantic status codes (200, 201, 400, 401, 404, etc.)

### API Endpoints

#### Authentication
```
POST   /api/auth/register          - Register new user
GET    /api/auth/me                - Get current user
PUT    /api/auth/me                - Update current user profile
```

#### Artworks
```
GET    /api/artworks               - List artworks (paginated)
POST   /api/artworks               - Create artwork (seller only)
GET    /api/artworks/{id}          - Get artwork details
PUT    /api/artworks/{id}          - Update artwork (seller only)
DELETE /api/artworks/{id}          - Delete artwork (seller/admin)
POST   /api/artworks/{id}/image    - Upload artwork image
```

#### Bids
```
GET    /api/bids                   - List bids (paginated)
POST   /api/bids                   - Place bid
GET    /api/bids/artwork/{id}      - Get bids for artwork
GET    /api/bids/user/{id}         - Get bids by user
```

#### Admin
```
GET    /api/admin/users            - List all users (admin only)
PUT    /api/admin/users/{id}/role  - Update user role (admin only)
DELETE /api/admin/users/{id}       - Delete user (admin only)
GET    /api/admin/artworks         - List all artworks (admin only)
DELETE /api/admin/artworks/{id}    - Delete artwork (admin only)
GET    /api/admin/audit-logs       - View audit logs (admin only)
GET    /api/admin/system/health    - System health (admin only)
```

#### Statistics
```
GET    /api/stats/platform         - Platform-wide statistics
GET    /api/stats/seller/{id}      - Seller statistics
GET    /api/stats/user/{id}        - User statistics
```

#### Health
```
GET/HEAD    /health                - Application health
GET/HEAD    /health/db             - Database connectivity
```

Note: Health endpoints support both GET and HEAD methods for compatibility with monitoring tools like UptimeRobot.

### Request/Response Format

#### Example: Create Artwork

**Request:**
```http
POST /api/artworks
Authorization: Bearer <jwt_token>
Content-Type: application/json

{
  "title": "Sunset Over Mountains",
  "description": "Beautiful landscape painting",
  "artist_name": "Jane Doe",
  "secret_threshold": 500.00,
  "category": "Landscape",
  "end_date": "2025-12-31T23:59:59Z"
}
```

**Response (201 Created):**
```json
{
  "id": 123,
  "title": "Sunset Over Mountains",
  "description": "Beautiful landscape painting",
  "artist_name": "Jane Doe",
  "seller_id": 456,
  "image_url": null,
  "secret_threshold": 500.00,
  "current_highest_bid": 0,
  "status": "ACTIVE",
  "category": "Landscape",
  "end_date": "2025-12-31T23:59:59Z",
  "created_at": "2025-11-24T10:00:00Z",
  "updated_at": "2025-11-24T10:00:00Z"
}
```

### Pagination

All list endpoints support pagination:

```
GET /api/artworks?skip=0&limit=10
```

**Response includes pagination metadata:**
```json
{
  "items": [...],
  "total": 100,
  "skip": 0,
  "limit": 10
}
```

### Error Responses

Standard error format:

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

---

## Security Architecture

### Defense in Depth

Multiple layers of security controls:

1. **Network Layer** - HTTPS/TLS encryption
2. **Application Layer** - Authentication, authorization, validation
3. **Data Layer** - SQL injection prevention, encrypted secrets
4. **Infrastructure Layer** - Container security, secret management

### Security Features

#### 1. Authentication & Authorization
- JWT-based authentication with Auth0
- Role-based access control (RBAC)
- Token validation on every request
- Secure token storage

#### 2. Input Validation
- Pydantic schemas on backend
- Zod schemas on frontend
- SQL injection prevention via ORM
- XSS prevention (React auto-escaping)

#### 3. Rate Limiting
- Sliding window algorithm
- Per-endpoint rate limits
- IP-based tracking
- 429 Too Many Requests response

#### 4. Security Headers
```python
# Applied via middleware
headers = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'"
}
```

#### 5. Audit Logging
- All user actions logged
- Admin actions tracked
- Security events recorded
- IP address and user agent captured

#### 6. Secret Management
- All secrets in environment variables
- No hardcoded credentials
- `.env` files gitignored
- Secret scanning in CI/CD

### Known Vulnerabilities

See [SECURITY.md](SECURITY.md) for comprehensive list of known security issues. **DO NOT deploy to production until critical vulnerabilities are resolved.**

---

## Infrastructure & DevOps

### Containerization

#### Docker Architecture

```
┌────────────────────────────────────────┐
│        Docker Compose Setup            │
├────────────────────────────────────────┤
│                                        │
│  ┌──────────────┐  ┌──────────────┐  │
│  │  Backend     │  │  Frontend    │  │
│  │  Container   │  │  Container   │  │
│  │              │  │              │  │
│  │  Python 3.11 │  │  Node 20     │  │
│  │  FastAPI     │  │  Vite/React  │  │
│  │  Port 8000   │  │  Port 5173   │  │
│  └──────┬───────┘  └──────────────┘  │
│         │                             │
│         │                             │
│  ┌──────┴────────────────────┐       │
│  │  PostgreSQL Container     │       │
│  │  Port 5432                │       │
│  │  Volume: postgres-data    │       │
│  └───────────────────────────┘       │
│                                        │
└────────────────────────────────────────┘
```

#### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:socket_app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Dockerfile

```dockerfile
FROM node:20-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
```

### CI/CD Pipeline

#### GitHub Actions Workflow

```yaml
# .github/workflows/backend-tests.yml
name: Backend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_DB: testdb
          POSTGRES_PASSWORD: testpass
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        run: |
          cd backend
          pytest --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./backend/coverage.xml
```

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Azure Cloud                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────────┐    ┌─────────────────────┐   │
│  │  Frontend           │    │  Backend            │   │
│  │  App Service        │    │  App Service        │   │
│  │  (Static/Node)      │    │  (Container)        │   │
│  │                     │    │                     │   │
│  │  https://gtw-       │    │  https://gtw-       │   │
│  │  frontend.azure     │    │  backend.azure      │   │
│  └─────────────────────┘    └─────────┬───────────┘   │
│                                        │               │
│                              ┌─────────┴───────────┐   │
│                              │  PostgreSQL         │   │
│                              │  Database           │   │
│                              │  (Managed Service)  │   │
│                              └─────────────────────┘   │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Performance & Scalability

### Performance Optimizations

#### 1. Database Optimizations
- **Indexes** on foreign keys and frequently queried fields
- **Eager Loading** to prevent N+1 queries
- **Connection Pooling** for efficient database connections
- **Query Optimization** with SQLAlchemy best practices

#### 2. API Optimizations
- **Pagination** to limit response sizes
- **Rate Limiting** to prevent abuse
- **Caching** (planned) for frequently accessed data
- **Compression** for response bodies

#### 3. Frontend Optimizations
- **Code Splitting** via Vite
- **Lazy Loading** for routes and components
- **Memoization** with React.memo and useMemo
- **Virtual Scrolling** (planned) for long lists

### Scalability Considerations

#### Horizontal Scaling
- **Stateless API** enables multiple backend instances
- **Load Balancer** distributes traffic across instances
- **Database Connection Pooling** manages concurrent connections

#### Vertical Scaling
- **Containerization** allows resource allocation adjustments
- **Database Scaling** through managed service upgrades

#### Bottlenecks
- **Database** - Primary bottleneck for high-traffic scenarios
  - Solution: Read replicas, caching layer
- **WebSocket Connections** - Limited by single server
  - Solution: Redis adapter for multi-server Socket.IO

---

## Monitoring & Observability

### Health Checks

#### Application Health
```
GET /health
Response: {"status": "healthy"}
```

#### Database Health
```
GET /health/db
Response: {"status": "healthy", "database": "connected"}
```

#### System Health (Admin)
```
GET /api/admin/system/health
Response: {
  "status": "healthy",
  "uptime": 3600,
  "database": "connected",
  "total_users": 150,
  "total_artworks": 75
}
```

### Error Tracking

**Sentry Integration** - Automatic error capture and reporting:
- Backend exceptions
- Frontend errors
- Performance monitoring
- Release tracking

### Uptime Monitoring

**UptimeRobot** - External monitoring:
- Backend API health checks
- Frontend availability checks
- Database connectivity checks
- Alert notifications via email/SMS

### Custom Health Dashboard

**Local Monitoring** - Real-time service status:
- Visual status indicators
- Response time tracking
- Service availability metrics
- Located at: [health-dashboard.html](health-dashboard.html)

### Logging

#### Application Logs
- Request/response logging
- Error logging with stack traces
- Performance logging (slow queries)

#### Audit Logs
- User actions (login, register, profile updates)
- Resource changes (artwork creation, bid placement)
- Admin actions (user management, artwork deletion)
- Security events (failed logins, unauthorized access)

---

## Design Decisions & Trade-offs

### 1. FastAPI vs Flask/Django
**Decision**: FastAPI
**Rationale**:
- Modern async/await support
- Automatic OpenAPI documentation
- Built-in data validation (Pydantic)
- High performance (on par with Node.js)

**Trade-off**: Smaller ecosystem than Django

### 2. React 19 vs Other Frameworks
**Decision**: React 19
**Rationale**:
- Large ecosystem and community
- Component-based architecture
- Excellent tooling and dev experience
- Team familiarity

**Trade-off**: Not as opinionated as frameworks like Next.js

### 3. Zustand vs Redux
**Decision**: Zustand
**Rationale**:
- Simpler API, less boilerplate
- Better TypeScript support
- Smaller bundle size
- Sufficient for application complexity

**Trade-off**: Less mature DevTools than Redux

### 4. PostgreSQL vs NoSQL
**Decision**: PostgreSQL
**Rationale**:
- ACID compliance for financial transactions (bids)
- Strong relational data model (users, artworks, bids)
- Mature tooling and ecosystem
- Team expertise

**Trade-off**: Less flexible schema than NoSQL

### 5. Auth0 vs Custom Authentication
**Decision**: Auth0
**Rationale**:
- Production-ready security
- OAuth/OIDC compliance
- Reduced development time
- Managed service (no security maintenance)

**Trade-off**: Vendor lock-in, monthly cost

### 6. Socket.IO vs WebSockets
**Decision**: Socket.IO
**Rationale**:
- Automatic reconnection
- Room/namespace support
- Fallback transports
- Easy integration with FastAPI

**Trade-off**: Larger client bundle than raw WebSockets

### 7. Monorepo vs Separate Repos
**Decision**: Monorepo
**Rationale**:
- Easier coordination between frontend/backend
- Shared documentation and CI/CD
- Simplified development workflow

**Trade-off**: Longer CI/CD times for monolithic pipeline

### 8. Docker Compose vs Kubernetes
**Decision**: Docker Compose (local), Azure App Services (production)
**Rationale**:
- Simpler local development
- Educational project scope
- Cost-effective for course project

**Trade-off**: Limited orchestration features compared to K8s

---

## Future Improvements

### Short-term
- Implement Stripe payment integration
- Add database seeding system
- Enhance error handling and user feedback
- Implement caching layer (Redis)

### Medium-term
- Email notifications for bid updates
- Advanced search and filtering
- User profile enhancements
- Performance monitoring dashboard

### Long-term
- Horizontal scaling with load balancer
- Read replicas for database
- CDN for static assets
- GraphQL API layer
- Mobile application (React Native)

---

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Socket.IO Documentation](https://socket.io/docs/)
- [Auth0 Documentation](https://auth0.com/docs)
- [Azure App Services Documentation](https://learn.microsoft.com/en-us/azure/app-service/)

---

**Last Updated:** 2025-11-24
**Version:** 1.0
**Maintained By:** Guess The Worth Development Team
