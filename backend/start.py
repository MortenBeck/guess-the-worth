#!/usr/bin/env python
"""
Startup script for Azure App Service.
Reads the PORT environment variable and starts uvicorn.
"""
import os
import subprocess
import sys

if __name__ == "__main__":
    # Run database migrations before starting the server
    print("Running database migrations...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            check=True,
            capture_output=True,
            text=True,
        )
        print("✓ Database migrations completed successfully")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print("✗ Database migration failed:", file=sys.stderr)
        print(e.stderr, file=sys.stderr)
        print("Continuing to start server anyway...", file=sys.stderr)
    except Exception as e:
        print(f"✗ Unexpected error during migration: {e}", file=sys.stderr)
        print("Continuing to start server anyway...", file=sys.stderr)

    port = int(os.getenv("PORT", "8000"))

    # Import uvicorn after setting up the environment
    import uvicorn

    # Binding to 0.0.0.0 is required for Docker containers
    # to accept external connections
    uvicorn.run(
        "main:socket_app", host="0.0.0.0", port=port, log_level="info"  # nosec B104
    )
