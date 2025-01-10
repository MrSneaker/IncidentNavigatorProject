import logging
from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.auth.models import User
from config import ApplicationConfig
from flask_sqlalchemy import SQLAlchemy

from routes import db
from routes.industry import industry
from routes.industry.models import populate_industries_from_mongo
from routes.llm import llm
from routes.auth import auth, session, bcrypt
from routes.chat import chat
from routes.llm import llm
from routes.config_llm import llmConf
from config import ApplicationConfig

config = ApplicationConfig()
app = Flask(__name__, static_folder='public')
app.config.from_object(config)

CORS(app,origins="*", supports_credentials=True)

# Add routes
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(chat, url_prefix='/chat')
app.register_blueprint(industry, url_prefix='/industry')
app.register_blueprint(llm, url_prefix='/llm')
app.register_blueprint(llmConf, url_prefix='/llm-conf')

def create_default_admin():
    admin_email = "admin@example.com"
    admin_username = "admin"
    admin_password = "admin"

    existing_admin = User.query.filter_by(email=admin_email).first()
    if existing_admin:
        logging.error("User admin already exist.")
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

# Initialize the app
with app.app_context():
    bcrypt.init_app(app)
    session.init_app(app)
    db.init_app(app)
    db.create_all()
    
    create_default_admin()
    populate_industries_from_mongo()

routes = [
    '/',
    '/login',
    '/register',
    '/chat',
    '/profile',
]

# each route will return the public/index.html file
# this is needed for react-router to work
for route in routes:
    app.add_url_rule(route, f'index_{route}', lambda: send_from_directory('public', 'index.html'))

@app.route('/<path:path>')
def files(path):
    return send_from_directory('public', path)

with app.app_context():
    bcrypt.init_app(app)
    session.init_app(app)  # Keep this if you need session management
    db.init_app(app)
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
