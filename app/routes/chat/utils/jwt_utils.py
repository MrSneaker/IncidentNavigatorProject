from flask import request, jsonify
import os
import datetime
import jwt

def generate_secret_key():
    return os.urandom(24)

SECRET_KEY = generate_secret_key()


def generate_jwt(username):
    payload = {
        'uid': username,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def verify_jwt(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return {"error": 1, "message": "Token expiré", 'payload': None}
    except jwt.InvalidTokenError:
        return {"error": 2, "message": "Token invalide", 'payload': None}
    except Exception as e:
        return {"error": -1, "message": str(e), 'payload': None}
    
    return {"error": 0, "message": "Token valide", 'payload': decoded}
    
def token_required(f):
    """Middleware pour protéger les routes avec JWT."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token manquant !'}), 401
        try:
            # Décoder et vérifier le token
            token = token.split(" ")[1]  # Retirer "Bearer "
            payload = verify_jwt(token)
            if not payload:
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            return {'error': 1, 'message': 'Token expiré', 'data': None}, 401
        except jwt.InvalidTokenError:
            return {'error': 2, 'message': 'Token invalide', 'data': None}, 401
        return f(*args, **kwargs)
    return decorated_function