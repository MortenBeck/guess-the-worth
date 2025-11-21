#!/usr/bin/env python
"""
Startup script for Azure App Service.
Reads the PORT environment variable and starts uvicorn.
"""
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))

    # Import uvicorn after setting up the environment
    import uvicorn

    # Binding to 0.0.0.0 is required for Docker containers to accept external connections
    uvicorn.run("main:socket_app", host="0.0.0.0", port=port, log_level="info")  # nosec B104
