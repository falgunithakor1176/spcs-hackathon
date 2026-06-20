from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

auth_bp = Blueprint('auth', __name__)

DEMO_ACCOUNTS = {
    'commissioner': {'password': 'admin123', 'role': 'Admin', 'name': 'Comm. R. K. Singh', 'badge': 'AHD-001'},
    'analyst': {'password': 'analyst123', 'role': 'Analyst', 'name': 'A. Patel', 'badge': 'AHD-142'},
    'officer': {'password': 'officer123', 'role': 'Officer', 'name': 'SI M. Joshi', 'badge': 'AHD-884'},
    'cyber': {'password': 'cyber123', 'role': 'Cyber', 'name': 'Insp. K. Shah', 'badge': 'AHD-401'},
}

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Missing JSON in request"}), 400
        
    username = data.get('username')
    password = data.get('password')

    user = DEMO_ACCOUNTS.get(username)
    if not user or user['password'] != password:
        return jsonify({"msg": "Bad username or password"}), 401

    claims = {
        'role': user['role'],
        'name': user['name'],
        'badge': user['badge']
    }

    access_token = create_access_token(identity=username, additional_claims=claims)
    refresh_token = create_refresh_token(identity=username, additional_claims=claims)

    return jsonify(
        access_token=access_token,
        refresh_token=refresh_token,
        user={'username': username, **claims}
    ), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    from flask_jwt_extended import get_jwt
    identity = get_jwt_identity()
    claims = get_jwt()
    new_claims = {
        'role': claims.get('role'),
        'name': claims.get('name'),
        'badge': claims.get('badge')
    }
    access_token = create_access_token(identity=identity, additional_claims=new_claims)
    return jsonify(access_token=access_token), 200

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    from flask_jwt_extended import get_jwt
    identity = get_jwt_identity()
    claims = get_jwt()
    return jsonify(user={
        'username': identity,
        'role': claims.get('role'),
        'name': claims.get('name'),
        'badge': claims.get('badge')
    }), 200
