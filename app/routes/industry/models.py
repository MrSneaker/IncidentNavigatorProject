import datetime
import logging
from uuid import uuid4
from .. import db
from .utils.retrieve_industries import get_industries

def get_uuid():
    """
    Generates a unique identifier (UUID) for new records.
    
    Returns:
        str: A unique hexadecimal UUID.
    """
    return uuid4().hex

class Industry(db.Model):
    """
    Represents the 'industries' table in the database.

    Attributes:
        id (str): A unique identifier for the industry (Primary Key).
        name (str): The name of the industry.
        created_at (datetime): Timestamp for when the industry record was created.
        updated_at (datetime): Timestamp for when the industry record was last updated.
    
    Methods:
        __repr__: Returns a string representation of the Industry object.
        to_dict: Converts the Industry object to a dictionary for easier JSON serialization.
        update_info: Updates the industry name and refreshes the 'updated_at' timestamp.
        get_industry: Retrieves an industry by either its ID or name.
        add_industry: Adds a new industry to the database.
        delete_industry: Deletes an industry from the database.
    """
    __tablename__ = 'industries'

    id = db.Column(db.String(32), primary_key=True, unique=True, default=get_uuid)
    name = db.Column(db.String(255), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def __repr__(self):
        """
        Returns a string representation of the Industry object.

        Returns:
            str: String representation of the Industry object.
        """
        return f'<Industry {self.name}>'

    def to_dict(self):
        """
        Converts the Industry object to a dictionary.

        Returns:
            dict: A dictionary representation of the Industry object with its id, name, created_at, and updated_at.
        """
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def update_info(self, name=None):
        """
        Updates the industry information, such as the name and the 'updated_at' timestamp.

        Args:
            name (str, optional): New name for the industry. If not provided, only the 'updated_at' field will be refreshed.
        """
        if name:
            self.name = name
        self.updated_at = datetime.datetime.now() 
        db.session.commit()

    @staticmethod
    def get_industry(id=None, name=None):
        """
        Retrieves an industry by either its ID or name.

        Args:
            id (str, optional): The ID of the industry.
            name (str, optional): The name of the industry.

        Returns:
            Industry or None: An Industry object if found, otherwise None.
        """
        if id is not None:
            return Industry.query.get(id)
        if name is not None:
            return Industry.query.filter_by(name=name).first()
        return None

    @staticmethod
    def add_industry(name):
        """
        Adds a new industry to the database.

        Args:
            name (str): The name of the industry.

        Returns:
            int: 0 if the industry was successfully added, 1 if the industry already exists.
        """
        industry = Industry.get_industry(name=name)
        if industry is not None:
            return 1

        industry = Industry(name=name)
        db.session.add(industry)
        db.session.commit()
        return 0

    @staticmethod
    def delete_industry(id):
        """
        Deletes an industry from the database by its ID.

        Args:
            id (str): The ID of the industry to delete.

        Returns:
            int: 0 if the industry was successfully deleted, 1 if the industry was not found.
        """
        industry = Industry.get_industry(id=id)
        if industry is None:
            return 1

        db.session.delete(industry)
        db.session.commit()
        return 0

def populate_industries_from_mongo():
    """
    Populates the 'industries' table from a list of industries retrieved from MongoDB.

    This function fetches the list of industries from the MongoDB database and adds them to
    the SQL database if they do not already exist.

    Exceptions:
        Handles any exceptions that may occur during the process and logs the error.
    """
    try:
        industries = get_industries()
        
        for industry_name in industries:
            if industry_name:
                if Industry.get_industry(name=industry_name) is None:
                    new_industry = Industry(name=industry_name)
                    db.session.add(new_industry)

        db.session.commit()
        print("Industries populated successfully.")
    except Exception as e:
        print(f"Error populating industries: {e}")
