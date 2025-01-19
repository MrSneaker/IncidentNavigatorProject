import datetime
import logging
from uuid import uuid4
from .. import db
from .utils.retrieve_industries import get_industries

# Function to generate a unique identifier (UUID) for new records.
def get_uuid():
    return uuid4().hex

# Industry model class to interact with the 'industries' table in the database.
class Industry(db.Model):
    __tablename__ = 'industries'

    # Column definitions for the 'industries' table.
    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    name = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    # String representation of the Industry object.
    def __repr__(self):
        return f'<Industry {self.name}>'

    # Convert the Industry object to a dictionary for easier JSON serialization.
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    # Method to update industry information (e.g., name).
    def update_info(self, name=None):
        if name:
            self.name = name
        self.updated_at = datetime.datetime.now() 
        db.session.commit()

    # Static method to retrieve an industry by either ID or name.
    @staticmethod
    def get_industry(id=None, name=None):
        if id is not None:
            return Industry.query.get(id)
        if name is not None:
            return Industry.query.filter_by(name=name).first()
        return None

    # Static method to add a new industry to the database.
    @staticmethod
    def add_industry(name):
        industry = Industry.get_industry(name=name)
        if industry is not None:
            return 1

        # If not, create a new industry record and add it to the session.
        industry = Industry(name=name)
        db.session.add(industry)
        db.session.commit()
        return 0

    # Static method to delete an industry by ID.
    @staticmethod
    def delete_industry(id):
        industry = Industry.get_industry(id=id)
        if industry is None:
            return 1

        db.session.delete(industry)
        db.session.commit()
        return 0

# Function to populate the 'industries' table from the list of industries retrieved from MongoDB.
def populate_industries_from_mongo():
    try:
        # Fetch the list of industries from MongoDB (using the previously defined function).
        industries = get_industries()
        
        # Loop through each industry name.
        for industry_name in industries:
            if industry_name:
                # Check if the industry already exists in the SQL database.
                if Industry.get_industry(name=industry_name) is None:
                    # If it doesn't exist, add it to the database.
                    new_industry = Industry(name=industry_name)
                    db.session.add(new_industry)

        db.session.commit()
        print("Industries populated successfully.")
    except Exception as e:
        # Print an error message if there is an issue populating the industries.
        print(f"Error populating industries: {e}")
