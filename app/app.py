import logging
from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.auth.models import User
from config import ApplicationConfig
from flask_sqlalchemy import SQLAlchemy

from routes import db
from routes.llm_config.models import LLMConfig
from routes.industry import industry
from routes.industry.models import populate_industries_from_mongo
from routes.llm import llm
from routes.auth import auth, session, bcrypt
from routes.chat import chat
from routes.llm import llm
from routes.llm_config import llmConf
from config import ApplicationConfig

config = ApplicationConfig()
app = Flask(__name__, static_folder='public')
app.config.from_object(config)

CORS(app, origins="*", supports_credentials=True)

app.register_blueprint(auth, url_prefix='/auth')      # Authentication routes
app.register_blueprint(chat, url_prefix='/chat')      # Chat functionality
app.register_blueprint(industry, url_prefix='/industry')  # Industry-related routes
app.register_blueprint(llm, url_prefix='/llm')        # Language Model routes
app.register_blueprint(llmConf, url_prefix='/llm-conf')  # LLM configuration routes

def create_default_admin():
    """
    Creates a default admin user if one doesn't already exist.
    This ensures there's always an admin account available for initial setup.
    """
    admin_email = "admin@example.com"
    admin_username = "admin"
    admin_password = "admin"

    existing_admin = User.query.filter_by(email=admin_email).first()
    if existing_admin:
        logging.info("User admin already exist.")
        return

    hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
    admin_user = User(
        email=admin_email,
        username=admin_username,
        password=hashed_password,
        admin=True
    )
    db.session.add(admin_user)
    db.session.commit()
    logging.info("Default Admin user created.")

routes = [
    '/',
    '/login',
    '/register',
    '/chat',
    '/profile',
    '/settings'
]

for route in routes:
    app.add_url_rule(route, f'index_{route}', lambda: send_from_directory('public', 'index.html'))

# Route to serve static files from the public directory
@app.route('/<path:path>')
def files(path):
    return send_from_directory('public', path)

with app.app_context():
    bcrypt.init_app(app)
    session.init_app(app)
    db.init_app(app)             
    db.create_all()
    
    # Initialize application data
    create_default_admin()
    populate_industries_from_mongo()
    
    # Configure default LLM (Language Learning Model)
    LLMConfig.add_llm(
        "https://api.groq.com/openai/v1/",
        "CHANGEME",
        "llama-3.3-70b-versatile",
        True
    )

if __name__ == '__main__':
    app.run(debug=True)
