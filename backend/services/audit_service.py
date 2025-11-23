"""
Audit logging service for tracking security-critical actions.
"""

from sqlalchemy.orm import Session
from models.audit_log import AuditLog
from models.user import User
from fastapi import Request
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """Service for logging security-critical actions."""

    @staticmethod
    def log_action(
        db: Session,
        action: str,
        resource_type: str,
        resource_id: Optional[int] = None,
        user: Optional[User] = None,
        details: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """
        Log a security-critical action.

        Args:
            action: Action performed (e.g., 'bid_placed', 'user_banned', 'artwork_sold')
            resource_type: Type of resource ('bid', 'artwork', 'user')
            resource_id: ID of the resource
            user: User who performed the action
            details: Additional details (JSON)
            request: FastAPI request object for IP/user-agent

        Returns:
            AuditLog: The created audit log entry, or None if logging failed
        """
        try:
            audit_log = AuditLog(
                user_id=user.id if user else None,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None,
            )

            db.add(audit_log)
            db.commit()
            db.refresh(audit_log)

            logger.info(
                f"Audit log created: {action} on {resource_type}:{resource_id} "
                f"by user {user.id if user else 'system'}"
            )

            return audit_log

        except Exception as e:
            logger.error(f"Failed to create audit log: {str(e)}")
            db.rollback()
            # Don't fail the main operation if audit logging fails
            return None
