from flask import request, jsonify
import os
import datetime
import jwt

# Function to generate a random secret key for JWT encoding/decoding.
def generate_secret_key():
    return os.urandom(24)

SECRET_KEY = generate_secret_key()

# Function to generate a JWT for a given username.
def generate_jwt(username):
    payload = {
        'uid': username, 
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    }
    # Encode the payload with the secret key using the HS256 algorithm.
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


# Function to verify a JWT and decode its payload.
def verify_jwt(token):
    try:
        # Decode the token using the secret key and verify its validity.
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        # Error returned if the token has expired.
        return {"error": 1, "message": "Token expiré", 'payload': None}
    except jwt.InvalidTokenError:
        # Error returned if the token is invalid.
        return {"error": 2, "message": "Token invalide", 'payload': None}
    except Exception as e:
        # Catch-all for other exceptions, returning the error message.
        return {"error": -1, "message": str(e), 'payload': None}
    
    # Return success message with the decoded payload if the token is valid.
    return {"error": 0, "message": "Token valide", 'payload': decoded}
    

# Decorator function to protect routes using JWT authentication.
def token_required(f):
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the token from the 'Authorization' header.
        token = request.headers.get('Authorization')
        if not token:
            # Return an error if no token is provided.
            return jsonify({'message': 'Token manquant !'}), 401
        try:
            # Split the token to remove "Bearer " prefix and verify it.
            token = token.split(" ")[1]  # Extract the token part after "Bearer".
            payload = verify_jwt(token)
            if not payload:
                # Raise an exception if payload verification fails.
                raise jwt.InvalidTokenError
        except jwt.ExpiredSignatureError:
            # Return error if the token has expired.
            return {'error': 1, 'message': 'Token expiré', 'data': None}, 401
        except jwt.InvalidTokenError:
            # Return error if the token is invalid.
            return {'error': 2, 'message': 'Token invalide', 'data': None}, 401
        # If the token is valid, proceed to the original function.
        return f(*args, **kwargs)
    return decorated_function
