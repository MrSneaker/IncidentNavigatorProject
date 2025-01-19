import os
from dotenv import load_dotenv
from datetime import timedelta
from routes.chat.utils.token import SECRET_KEY
import redis

load_dotenv()

INSTALL_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'install') 
SQLALCHEMY_DATABASE_FOLDER = os.path.join(INSTALL_FOLDER, 'instance')
if not os.path.exists(SQLALCHEMY_DATABASE_FOLDER):
    os.makedirs(SQLALCHEMY_DATABASE_FOLDER)
    
class ApplicationConfig:
    SECRET_KEY = SECRET_KEY
    
       
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(INSTALL_FOLDER, "instance", "db.sqlite")}'
    SQLALCHEMY_BINDS = {
        'user': f'sqlite:///{os.path.join(INSTALL_FOLDER, "instance", "user.sqlite")}',
        'chat': f'sqlite:///{os.path.join(INSTALL_FOLDER, "instance", "chat.sqlite")}'
    }
        
    SESSION_TYPE = 'redis'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_REDIS = redis.from_url("redis://127.0.0.1:6379")
    SESSION_COOKIE_SAMESITE = 'Strict'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)