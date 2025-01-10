import datetime
import logging
from uuid import uuid4

from .. import db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)


def get_uuid():
    return uuid4().hex


user_industry = db.Table(
    'user_industry',
    db.Column('user_id', db.String(32), db.ForeignKey(
        'users.id'), primary_key=True),
    db.Column('industry_id', db.String(32), db.ForeignKey(
        'industries.id'), primary_key=True)
)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String(32), primary_key=True,
                   unique=True, default=get_uuid)
    email = db.Column(db.String(345), unique=True, nullable=False)
    username = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    industries = db.relationship(
        'Industry', secondary=user_industry, backref='users', lazy='dynamic'
    )
    admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'industries': self.industries,
            'admin': self.admin,
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

    def set_admin(self, is_admin):
        self.admin = is_admin
        self.updated_at = datetime.datetime.now()
        db.session.commit()

    def update_industries(self, new_industries):
        from ..industry.models import Industry

        self.industries = []

        for industry in new_industries:
            industry_name = industry.get('name', None)
            industry = Industry.query.filter_by(name=industry_name).first()
            self.industries.append(industry)

        db.session.commit()

    @staticmethod
    def get_user(id=None, email=None):
        if id is not None:
            return User.query.get(id)
        if email is not None:
            return User.query.filter_by(email=email).first()
        return None

    @staticmethod
    def register(email, username, password, admin=False):
        user = User.get_user(email=email)
        if user is not None:
            return 1

        print(email, username, password)
        user = User(email=email, username=username,
                    password=password, admin=admin)
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

    @staticmethod
    def delete(user_id):
        user = User.get_user(id=user_id)
        if user is None:
            return 1 

        try:
            user.industries = []

            db.session.delete(user)
            db.session.commit()
            return 0 
        except Exception as e:
            logging.error(f"Error while deleting user {user_id}: {str(e)}")
            db.session.rollback()
            return 2 
