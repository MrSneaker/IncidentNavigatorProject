import logging
from flask import request, session
from . import auth, bcrypt
from .models import User
from ..chat.utils.jwt_utils import generate_jwt


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

@auth.route('/@me', methods=['GET'])
def me():
    user_id = session.get('user_id', None)
    if user_id is None:
        return {'error': 1, 'message': 'Unauthorized', 'data': None}, 201
    user = User.get_user(id=user_id)
    if user is None:
        return {'error': 2, 'message': 'User not found', 'data': None}, 202
    
    industries_list = [industry.to_dict() for industry in user.industries]
    
    return {'error': 0, 'message': 'User found', 'data': {
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'industries': industries_list,
        'isAdmin': user.admin,
        'created_at': user.created_at,
        'updated_at': user.updated_at
    }}, 200
    
@auth.route('/register', methods=['POST'])
def register():
    email = request.json.get('email', None)
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    if not email:
        return {'error': 1, 'message': 'Email is required', 'data': None}, 400
    if not username:
        return {'error': 2, 'message': 'Username is required', 'data': None}, 400
    if not password:
        return {'error': 3, 'message': 'Password is required', 'data': None}, 400
    
    hased_password = bcrypt.generate_password_hash(password)
    err = User.register(email, username, hased_password)
    if not err:
        return {'error': 0, 'message': 'User registered', 'data': None}, 201
    return {
        1: {'error': 4, 'message': 'User already exists', 'data': None},
    }.get(err, {'error': 5, 'message': 'Unknown error', 'data': None}), 400

@auth.route('/login', methods=['POST'])
def login():
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    if not email:
        return {'error': 1, 'message': 'Email is required', 'data': None}, 400
    if not password:
        return {'error': 2, 'message': 'Password is required', 'data': None}, 400
    user: User = User.get_user(email=email)
    err = 1 if user is None else 2 if not bcrypt.check_password_hash(user.password, password) else 0
    if not err:
        token = generate_jwt(user.id)  
        session['user_id'] = user.id
        session['email'] = user.email
        session['username'] = user.username
        session['token'] = token
        return {'error': 0, 'message': 'User logged in', 'data': {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'token': token
        }}, 200
    return {
        1: {'error': 3, 'message': 'User not found', 'data': None},
        2: {'error': 4, 'message': 'Incorrect password', 'data': None}
    }.get(err, {'error': 5, 'message': 'Unknown error', 'data': None}), 404
    
@auth.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    session.pop('email', None)
    session.pop('username', None)
    session.pop('token', None)
    return {'error': 0, 'message': 'User logged out', 'data': None}, 200

@auth.route('/rename', methods=['POST'])
def rename():
    user_id = session.get('user_id', None)
    if user_id is None:
        return {'error': 1, 'message': 'Unauthorized', 'data': None}, 201
    user: User = User.get_user(id=user_id)
    if user is None:
        return {'error': 2, 'message': 'User not found', 'data': None}, 202
    username = request.json.get('username', None)
    if not username:
        return {'error': 3, 'message': 'Username is required', 'data': None}, 400
    user.rename(username)
    return {'error': 0, 'message': 'Username changed', 'data': None}, 200

@auth.route('/token', methods=['POST'])
def refresh_token():
    user_id = session.get('user_id', None)
    if user_id is None:
        return {'error': 1, 'message': 'Unauthorized', 'data': None}, 201
    user: User = User.get_user(id=user_id)
    if user is None:
        return {'error': 2, 'message': 'User not found', 'data': None}, 202
    token = generate_jwt(user.username)
    return {'error': 0, 'message': 'Token refreshed', 'data': {
        'token': token
    }}, 200
    
    
@auth.route('/users', methods=['GET'])
def get_users():
    user_id = session.get('user_id', None)
    if user_id is None:
        return {'error': 1, 'message': 'Unauthorized', 'data': None}, 401

    user = User.get_user(id=user_id)
    if user is None or not user.admin:
        return {'error': 2, 'message': 'Permission denied', 'data': None}, 403

    users = User.query.all()
    data = [{
        'id': u.id,
        'email': u.email,
        'username': u.username,
        'industries': [industry.to_dict() for industry in u.industries],
        'isAdmin': u.admin,
        'created_at': u.created_at,
        'updated_at': u.updated_at
    } for u in users]

    return {'error': 0, 'message': 'Users retrieved', 'data': data}, 200


@auth.route('/users/<user_id>/industries', methods=['PUT'])
def update_user_industries(user_id):
    admin_id = session.get('user_id', None)
    if admin_id is None:
        return {'error': 1, 'message': 'Unauthorized', 'data': None}, 401

    admin_user = User.get_user(id=admin_id)
    if admin_user is None or not admin_user.admin:
        return {'error': 2, 'message': 'Permission denied', 'data': None}, 403

    user = User.get_user(id=user_id)
    if user is None:
        return {'error': 3, 'message': 'User not found', 'data': None}, 404

    industries = request.json.get('industries', None)
    logging.error('industries : ', industries)
    if industries is None or not isinstance(industries, list):
        return {'error': 4, 'message': 'Invalid industries format', 'data': None}, 400
    
    user.update_industries(industries)

    return {'error': 0, 'message': 'Industries updated', 'data': None}, 200


@auth.route('/check-admin', methods=['GET'])
def check_admin():
    user_id = session.get('user_id', None)
    if user_id is None:
        return {'error': 1, 'message': 'Unauthorized', 'isAdmin': False}, 401

    user = User.get_user(id=user_id)
    if user is None:
        return {'error': 2, 'message': 'User not found', 'isAdmin': False}, 404

    return {'error': 0, 'message': 'Admin status checked', 'isAdmin': user.admin}, 200
    
@auth.route('/delete', methods=['DELETE'])
def delete_user():
    user_id = session.get('user_id', None)
    if user_id is None:
        return {'error': 1, 'message': 'Unauthorized', 'isAdmin': False}, 401

    user = User.get_user(id=user_id)
    if user is None:
        return {'error': 2, 'message': 'User not found', 'isAdmin': False}, 404

    admin_user = User.get_user(id=user_id)
    if admin_user is None or not admin_user.admin:
        return {'error': 2, 'message': 'Permission denied', 'data': None}, 403

    data = request.get_json()
    user_to_delete_id = data.get('user_id')

    if not user_to_delete_id:
        return {'error': 4, 'message': 'User ID is required'}, 400

    try:
        User.delete(user_to_delete_id)
        return {'success': True, 'message': 'User deleted successfully'}, 200
    except Exception as e:
        return {'error': 6, 'message': f'Error while deleting user: {str(e)}'}, 500