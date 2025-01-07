from flask import request, session
from . import auth, bcrypt
from .models import User
from ..chat.utils.jwt_utils import generate_jwt


@auth.route('/@me', methods=['GET'])
def me():
    user_id = session.get('user_id', None)
    if user_id is None:
        return {'error': 1, 'message': 'Unauthorized', 'data': None}, 201
    user = User.get_user(id=user_id)
    if user is None:
        return {'error': 2, 'message': 'User not found', 'data': None}, 202
    return {'error': 0, 'message': 'User found', 'data': {
        'id': user.id,
        'email': user.email,
        'username': user.username,
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
    
    