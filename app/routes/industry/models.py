import datetime
import logging
from uuid import uuid4
from .. import db
from .utils.retrieve_industries import get_industries

def get_uuid():
    return uuid4().hex

class Industry(db.Model):
    __tablename__ = 'industries'
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    name = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        return f'<Industry {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def update_info(self, name=None):
        if name:
            self.name = name
        self.updated_at = datetime.datetime.now()
        db.session.commit()

    @staticmethod
    def get_industry(id=None, name=None):
        if id is not None:
            return Industry.query.get(id)
        if name is not None:
            return Industry.query.filter_by(name=name).first()
        return None

    @staticmethod
    def add_industry(name):
        industry = Industry.get_industry(name=name)
        if industry is not None:
            return 1  # Industry already exists

        industry = Industry(name=name)
        db.session.add(industry)
        db.session.commit()
        return 0

    @staticmethod
    def delete_industry(id):
        industry = Industry.get_industry(id=id)
        if industry is None:
            return 1  # Industry not found

        db.session.delete(industry)
        db.session.commit()
        return 0

def populate_industries_from_mongo():
    try:
        industries = get_industries()
        
        for industry_name in industries:
            if industry_name:
                # Add to SQLAlchemy database if not already present
                if Industry.get_industry(name=industry_name) is None:
                    new_industry = Industry(name=industry_name)
                    db.session.add(new_industry)

        db.session.commit()
        print("Industries populated successfully.")
    except Exception as e:
        print(f"Error populating industries: {e}")