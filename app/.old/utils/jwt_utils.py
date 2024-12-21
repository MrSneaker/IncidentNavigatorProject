import datetime
import jwt

SECRET_KEY = "SECRET_KEY" # TODO Replace by a real secret key


def generate_jwt(username):
    secret_key = SECRET_KEY
    payload = {
        'username': username,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    }
    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


def verify_jwt(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return decoded
    except jwt.ExpiredSignatureError:
        return {"error": "Token expiré"}
    except jwt.InvalidTokenError:
        return {"error": "Token invalide"}