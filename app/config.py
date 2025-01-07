from dotenv import load_dotenv
from datetime import timedelta
from routes.chat.utils.jwt_utils import SECRET_KEY
import os
import redis

load_dotenv()

class ApplicationConfig:
    SECRET_KEY = SECRET_KEY
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///./db.sqlite'
    SQLALCHEMY_BINDS = {
        'user': 'sqlite:///./user.sqlite',
        'chat': 'sqlite:///./chat.sqlite'
    }
        
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.from_url("redis://127.0.0.1:6379")
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)