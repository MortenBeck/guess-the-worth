import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from config.settings import settings

# Enable SQL query logging in development
# Set ENVIRONMENT=development in .env to enable query logging
echo_sql = os.getenv("ENVIRONMENT", "development") == "development"

# Azure-optimized database configuration
# Use connection pooling for production, NullPool for development
engine_kwargs = {
    "pool_pre_ping": True,  # Verify connections before using them
    "pool_recycle": 3600,  # Recycle connections after 1 hour
    "echo": echo_sql,  # Enable SQL query logging in development
}

# Configure connection pool based on environment
if (
    "azure" in settings.database_url.lower()
    or "postgres.database.azure.com" in settings.database_url
):
    # Azure PostgreSQL optimizations
    engine_kwargs.update(
        {
            "poolclass": QueuePool,
            "pool_size": 5,  # Number of connections to keep open
            "max_overflow": 10,  # Additional connections when pool is full
            "pool_timeout": 30,  # Timeout for getting a connection from pool
        }
    )
else:
    # Local development - use NullPool to avoid connection issues
    engine_kwargs["poolclass"] = NullPool

engine = create_engine(settings.database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
