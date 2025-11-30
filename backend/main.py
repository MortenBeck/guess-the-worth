import os
from contextlib import asynccontextmanager

import sentry_sdk
import socketio
from config.settings import settings
from database import engine
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from middleware.rate_limit import setup_rate_limiting
from middleware.security_headers import SecurityHeadersMiddleware
from models.base import Base
from routers import admin, artworks, auth, bids, health, payments, stats, users
from services.auth_service import AuthService
from services.jwt_service import JWTService

# Initialize Sentry
sentry_dsn = os.getenv("SENTRY_DSN")
if sentry_dsn:
    sentry_sdk.init(
        dsn=sentry_dsn,
        traces_sample_rate=0.1,  # 10% of transactions for performance monitoring
        profiles_sample_rate=0.1,  # 10% of transactions for profiling
        send_default_pii=True,  # Send user IP and request data
        environment=os.getenv("ENVIRONMENT", "production"),
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: cleanup if needed (none required currently)


app = FastAPI(title="Guess The Worth API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure rate limiting
setup_rate_limiting(app)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

sio = socketio.AsyncServer(
    async_mode="asgi", cors_allowed_origins=settings.allowed_origins
)

socket_app = socketio.ASGIApp(sio, app)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(artworks.router, prefix="/api/artworks", tags=["artworks"])
app.include_router(bids.router, prefix="/api/bids", tags=["bids"])
app.include_router(payments.router, prefix="/api/payments", tags=["payments"])
app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
app.include_router(admin.router)

# Mount static files for image uploads
# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/")
async def root():
    return {"message": "Guess The Worth API"}


@sio.event
async def connect(sid, environ):
    """
    Handle WebSocket connection with JWT authentication.

    SECURITY: Validates JWT token before allowing connection.
    Disconnects client if authentication fails.
    """
    # Extract token from query parameters or headers
    query_string = environ.get("QUERY_STRING", "")
    token = None

    # Parse query string for token
    if "token=" in query_string:
        for param in query_string.split("&"):
            if param.startswith("token="):
                token = param.split("=", 1)[1]
                break

    # If no token in query, try Authorization header
    if not token:
        auth_header = environ.get("HTTP_AUTHORIZATION", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]

    if not token:
        print(f"Client {sid} connection rejected: No token provided")
        await sio.disconnect(sid)
        return False

    # Verify token (try Auth0 first, then JWT)
    user_id = None
    try:
        # Try Auth0 token
        auth_user = AuthService.verify_auth0_token(token)
        if auth_user:
            user_id = auth_user.sub
    except Exception:
        # Try JWT token
        try:
            payload = JWTService.verify_token(token)
            if payload:
                user_id = payload.get("sub")
        except Exception:
            pass

    if not user_id:
        print(f"Client {sid} connection rejected: Invalid token")
        await sio.disconnect(sid)
        return False

    # Store user_id in session for later use
    async with sio.session(sid) as session:
        session["user_id"] = user_id

    print(f"Client {sid} connected (user: {user_id})")


@sio.event
async def disconnect(sid):
    print(f"Client {sid} disconnected")


@sio.event
async def join_artwork(sid, data):
    artwork_id = data.get("artwork_id")
    await sio.enter_room(sid, f"artwork_{artwork_id}")
    print(f"Client {sid} joined artwork {artwork_id}")


@sio.event
async def leave_artwork(sid, data):
    artwork_id = data.get("artwork_id")
    await sio.leave_room(sid, f"artwork_{artwork_id}")
    print(f"Client {sid} left artwork {artwork_id}")


if __name__ == "__main__":
    import uvicorn

    # nosec B104: Binding to 0.0.0.0 is required for Docker containers
    # to accept external connections
    uvicorn.run("main:socket_app", host="0.0.0.0", port=8000, reload=True)  # nosec B104
