"""
audit_service.py — Audit Logging Service
=========================================
Call log_action() from any route to record a system event.
Never modifies existing audit entries — append-only.
"""

import logging
from datetime import datetime
from flask import request as flask_request

logger = logging.getLogger(__name__)


def log_action(username: str, role: str, action: str, resource: str = None, detail: str = None):
    """
    Write one row to audit_logs.
    Safe to call — silently skips on any DB error to never break a route.

    Args:
        username : The logged-in username
        role     : Their role (Admin / Analyst / Officer / Cyber)
        action   : Event type e.g. LOGIN, LOGOUT, ENGINE_RUN, EXPORT, ACK_ALERT
        resource : What was accessed e.g. 'Engine 2', '/api/crimes', 'Analytics'
        detail   : Optional free-text context
    """
    try:
        from db import db
        from models import AuditLog

        ip = None
        try:
            ip = flask_request.remote_addr
        except RuntimeError:
            pass  # outside request context

        entry = AuditLog(
            username   = username or 'unknown',
            role       = role or '',
            action     = action,
            resource   = resource or '',
            detail     = detail or '',
            ip_address = ip,
            timestamp  = datetime.utcnow(),
        )
        db.session.add(entry)
        db.session.commit()
    except Exception as e:
        logger.warning(f"[AuditLog] Failed to write audit entry: {e}")
