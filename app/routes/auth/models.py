import datetime
import logging
from uuid import uuid4

from .. import db

# Configure logging to show timestamps, logger name, level, and message
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

# Helper function to generate unique IDs for users
def get_uuid():
    """Generate a unique hexadecimal UUID for user identification."""
    return uuid4().hex

# Junction table for many-to-many relationship between users and industries
user_industry = db.Table(
    'user_industry',
    db.Column('user_id', db.String(32), db.ForeignKey(
        'users.id'), primary_key=True),
    db.Column('industry_id', db.String(32), db.ForeignKey(
        'industries.id'), primary_key=True)
)

class User(db.Model):
    """
    User model representing application users.
    
    Attributes:
        id: Unique identifier for the user
        email: User's email address (unique)
        username: User's display name
        password: Hashed password
        industries: Related industries for the user
        admin: Boolean flag for admin privileges
        created_at: Timestamp of user creation
        updated_at: Timestamp of last update
    """
    __tablename__ = 'users'
    
    # Primary user identification fields
    id = db.Column(db.String(32), primary_key=True,
                   unique=True, default=get_uuid)
    email = db.Column(db.String(345), unique=True, nullable=False)
    username = db.Column(db.Text, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
    # Relationships and permissions
    industries = db.relationship(
        'Industry', 
        secondary=user_industry,
        backref='users',
        lazy='dynamic'
    )
    admin = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(
        db.DateTime, 
        default=datetime.datetime.now, 
        onupdate=datetime.datetime.now
    )

    def __repr__(self):
        """String representation of the user."""
        return f'<User {self.username}>'

    def to_dict(self):
        """
        Convert user object to dictionary for API responses.
        Excludes sensitive information like password.
        """
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
        """Update the user's username."""
        self.username = username
        self.updated_at = datetime.datetime.now()
        db.session.commit()

    def change_password(self, password):
        """Update the user's password."""
        self.password = password
        self.updated_at = datetime.datetime.now()
        db.session.commit()

    def set_admin(self, is_admin):
        """Update the user's admin status."""
        self.admin = is_admin
        self.updated_at = datetime.datetime.now()
        db.session.commit()

    def update_industries(self, new_industries):
        """
        Update user's associated industries.
        
        Args:
            new_industries: List of industry dictionaries with 'name' field
        """
        from ..industry.models import Industry

        # Clear existing industries
        self.industries = []

        # Add new industries
        for industry in new_industries:
            industry_name = industry.get('name', None)
            industry = Industry.query.filter_by(name=industry_name).first()
            self.industries.append(industry)

        db.session.commit()

    @staticmethod
    def get_user(id=None, email=None):
        """
        Retrieve a user by ID or email.
        
        Args:
            id: User's unique identifier
            email: User's email address
            
        Returns:
            User object or None if not found
        """
        if id is not None:
            return User.query.get(id)
        if email is not None:
            return User.query.filter_by(email=email).first()
        return None

    @staticmethod
    def register(email, username, password, admin=False):
        """
        Register a new user.
        
        Args:
            email: User's email address
            username: User's display name
            password: User's password (should be pre-hashed)
            admin: Boolean indicating admin status
            
        Returns:
            0: Success
            1: User already exists
        """
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
        """
        Authenticate a user.
        
        Args:
            email: User's email address
            password: User's password (should be pre-hashed)
            
        Returns:
            0: Success
            1: User not found
            2: Invalid password
        """
        user: User = User.get_user(email=email)
        if user is None:
            return 1
        if user.password != password:
            return 2
        return 0

    @staticmethod
    def delete(user_id):
        """
        Delete a user and their relationships.
        
        Args:
            user_id: ID of user to delete
            
        Returns:
            0: Success
            1: User not found
            2: Error during deletion
        """
        user = User.get_user(id=user_id)
        if user is None:
            return 1 

        try:
            # Remove industry relationships first
            user.industries = []

            # Delete the user
            db.session.delete(user)
            db.session.commit()
            return 0 
        except Exception as e:
            logging.error(f"Error while deleting user {user_id}: {str(e)}")
            db.session.rollback()
            return 2