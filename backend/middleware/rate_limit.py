"""
Rate limiting middleware using SlowAPI.
Prevents DoS attacks and API abuse.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

# Initialize limiter
# For development: in-memory storage
# For production: use Redis (change to redis://localhost:6379)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per minute"],  # Global default
    storage_uri="memory://",  # Change to redis:// in production
)

async def rate_limit_exceeded_handler(
    request: Request,
    exc: RateLimitExceeded
) -> JSONResponse:
    """Custom handler for rate limit exceeded errors."""
    logger.warning(
        f"Rate limit exceeded for {request.client.host} "
        f"on {request.url.path}"
    )
    return JSONResponse(
        status_code=429,
        content={
            "error": "Rate limit exceeded",
            "message": "Too many requests. Please try again later.",
            "retry_after": exc.detail,
        },
        headers={"Retry-After": str(exc.detail)},
    )

def setup_rate_limiting(app):
    """Configure rate limiting for the application."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)
    logger.info("Rate limiting configured successfully")
