from flask import Flask, send_from_directory
from config import ApplicationConfig
from flask_sqlalchemy import SQLAlchemy

from routes import db
from routes.auth import auth, session, cors, bcrypt
from routes.chat import chat

config = ApplicationConfig()
app = Flask(__name__, static_folder='public')
app.config.from_object(config)

# Add /auth and /chat routes
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(chat, url_prefix='/chat')
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
    # Initialize bcrypt
    bcrypt.init_app(app)
    
    # Initialize cors
    cors.init_app(app)
    
    # Initialize session
    session.init_app(app)
    
    # Init databases
    db.init_app(app)
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    app.run(debug=True)