import datetime
from uuid import uuid4

from .. import db

def get_uuid():
    return uuid4().hex


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    email = db.Column(db.String(345), unique=True, nullable=False)
    username = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)    
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
    def rename(self, username):
        self.username = username
        self.updated_at = datetime.datetime.now()
        db.session.commit()
    
    def change_password(self, password):
        self.password = password
        self.updated_at = datetime.datetime.now()
        db.session.commit()
        
    @staticmethod
    def get_user(id=None, email=None):
        if id is not None:
            return User.query.get(id)
        if email is not None:
            return User.query.filter_by(email=email).first()
        return None

    @staticmethod
    def register(email, username, password):
        user = User.get_user(email=email)
        if user is not None:
            return 1
        
        print(email, username, password)
        user = User(email=email, username=username, password=password)
        db.session.add(user)
        db.session.commit()
        return 0
        
    @staticmethod
    def login(email, password):
        user: User = User.get_user(email=email)
        if user is None:
            return 1
        if user.password != password:
            return 2
        return 0
