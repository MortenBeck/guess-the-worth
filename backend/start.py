#!/usr/bin/env python
"""
Startup script for Azure App Service.
Reads the PORT environment variable and starts uvicorn.
"""
import os
import sys

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))

    # Import uvicorn after setting up the environment
    import uvicorn

    uvicorn.run(
        "main:socket_app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
