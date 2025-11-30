from database import get_db
from fastapi import APIRouter, Depends, status
from sqlalchemy import text
from sqlalchemy.orm import Session

router = APIRouter()


@router.api_route("/", methods=["GET", "HEAD"], status_code=status.HTTP_200_OK)
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": "guess-the-worth-backend",
    }


@router.api_route("/db", methods=["GET", "HEAD"], status_code=status.HTTP_200_OK)
async def database_health_check(db: Session = Depends(get_db)):
    """Health check that verifies database connectivity"""
    try:
        # Execute a simple query to verify database connection
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
        }
