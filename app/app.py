from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from routes import db
from routes.auth import auth, session, bcrypt
from routes.chat import chat
from routes.llm import llm
from config import ApplicationConfig

config = ApplicationConfig()
app = Flask(__name__, static_folder='public')
app.config.from_object(config)

CORS(app,origins="*", supports_credentials=True)

# Add /auth and /chat routes
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(chat, url_prefix='/chat')
app.register_blueprint(llm, url_prefix='/llm')
routes = [
    '/',
    '/login',
    '/register',
    '/chat',
    '/chat/<path:path>',
    '/profile',
]

# each reoute will return the public/index.html file
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
