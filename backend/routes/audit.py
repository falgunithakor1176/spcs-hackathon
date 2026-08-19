"""
audit.py — Audit Log API Endpoints
====================================
GET /api/audit/logs  — Returns paginated audit log (Admin role only)
GET /api/audit/stats — Summary counts by action type
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from models import AuditLog
from sqlalchemy import desc

audit_bp = Blueprint('audit', __name__)


def _require_admin():
    claims = get_jwt()
    role = claims.get('role', '')
    if role not in ('Admin', 'Commissioner'):
        return jsonify({'status': 'error', 'message': 'Admin access required'}), 403
    return None


@audit_bp.route('/audit/logs', methods=['GET'])
@jwt_required()
def get_audit_logs():
    """
    GET /api/audit/logs?page=1&limit=50&action=LOGIN&role=Officer
    Returns paginated audit log entries, newest first.
    Accessible by Admin/Commissioner role only.
    """
    err = _require_admin()
    if err:
        return err

    page    = request.args.get('page',   1,    type=int)
    limit   = min(request.args.get('limit', 100, type=int), 200)
    action  = request.args.get('action', None)
    role    = request.args.get('role',   None)
    username= request.args.get('username', None)

    q = AuditLog.query.order_by(desc(AuditLog.timestamp))
    if action:
        q = q.filter(AuditLog.action == action.upper())
    if role:
        q = q.filter(AuditLog.role == role)
    if username:
        q = q.filter(AuditLog.username.ilike(f'%{username}%'))

    total  = q.count()
    offset = (page - 1) * limit
    rows   = q.offset(offset).limit(limit).all()

    return jsonify({
        'status': 'success',
        'total':  total,
        'page':   page,
        'limit':  limit,
        'data':   [r.to_dict() for r in rows],
    }), 200


@audit_bp.route('/audit/stats', methods=['GET'])
@jwt_required()
def get_audit_stats():
    """
    GET /api/audit/stats
    Returns count per action type and per role for summary display.
    """
    err = _require_admin()
    if err:
        return err

    from sqlalchemy import func
    from db import db

    action_counts = db.session.query(
        AuditLog.action,
        func.count(AuditLog.id).label('count')
    ).group_by(AuditLog.action).all()

    role_counts = db.session.query(
        AuditLog.role,
        func.count(AuditLog.id).label('count')
    ).group_by(AuditLog.role).all()

    total = AuditLog.query.count()

    return jsonify({
        'status':        'success',
        'total_entries': total,
        'by_action':     {a: c for a, c in action_counts},
        'by_role':       {r: c for r, c in role_counts},
    }), 200
