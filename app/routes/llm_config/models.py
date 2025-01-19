import datetime
import logging
import os
from uuid import uuid4
from cryptography.fernet import Fernet
from dotenv import load_dotenv

from .. import db

dotenv_path = "app/routes/llm_config/.env"
load_dotenv(dotenv_path)

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    # Notify that a new key will be generated
    print("SECRET_KEY not found in .env. Generating a new one...")
    SECRET_KEY = Fernet.generate_key().decode("utf-8")
    # Append the new SECRET_KEY to the .env file for future use
    with open(dotenv_path, "a") as dotenv_file:
        dotenv_file.write(f"SECRET_KEY={SECRET_KEY}\n")
    print("New SECRET_KEY saved to .env")

# Initialize the cipher suite for encryption and decryption using the SECRET_KEY
cipher_suite = Fernet(SECRET_KEY)

# Function to generate a unique identifier
def get_uuid():
    return uuid4().hex


# Define a database model for LLM (Large Language Model) configurations
class LLMConfig(db.Model):
    __tablename__ = 'llm'  # Define the table name

    # Define columns in the database table
    id = db.Column(db.String(32), primary_key=True,
                   unique=True, default=get_uuid)  # Primary key with unique UUID
    model = db.Column(db.String(255), nullable=False, unique=True)  # Model name, must be unique
    uri = db.Column(db.String(255), nullable=False, unique=False)  # URI of the model
    api_key_encrypted = db.Column(db.String(255), nullable=False)  # Encrypted API key
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)  # Timestamp for creation
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)  # Timestamp for updates
    selected = db.Column(db.Boolean, default=False, nullable=False)  # Boolean flag for selection

    # Convert the model instance to a dictionary for serialization
    def to_dict(self):
        return {
            'id': self.id,
            'uri': self.uri,
            'model': self.model,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'api_key': self.get_partial_api_key(),  # Partially masked API key
            'selected': self.selected
        }

    # Constructor to initialize the LLMConfig object
    def __init__(self, uri, api_key, model, selected):
        self.uri = uri
        self.api_key_encrypted = self._encrypt_api_key(api_key)  # Encrypt the API key
        self.model = model
        self.selected = selected

    # Encrypt the API key using the cipher suite
    def _encrypt_api_key(self, api_key):
        return cipher_suite.encrypt(api_key.encode('utf-8')).decode('utf-8')

    # Decrypt the API key using the cipher suite
    def _decrypt_api_key(self):
        return cipher_suite.decrypt(self.api_key_encrypted.encode('utf-8')).decode('utf-8')

    # Return the first 8 characters of the decrypted API key for partial display
    def get_partial_api_key(self):
        api_key = self._decrypt_api_key()
        return api_key[:8]

    # Verify if a given API key matches the stored encrypted key
    def check_api_key(self, api_key):
        return api_key == self._decrypt_api_key()

    # Update the URI of the model and commit the changes to the database
    def update_uri(self, new_uri):
        self.uri = new_uri
        self.updated_at = datetime.datetime.now()
        db.session.commit()

    # Update the API key of the model and commit the changes to the database
    def update_api_key(self, new_api_key):
        self.api_key_encrypted = self._encrypt_api_key(new_api_key)
        self.updated_at = datetime.datetime.now()
        db.session.commit()

    # Static method to add a new LLM configuration to the database
    @staticmethod
    def add_llm(uri, api_key, model, selected):
        # Check if an LLM with the same model name already exists
        existing_llm = LLMConfig.query.filter_by(model=model).first()
        if existing_llm:
            return {'error': 1, 'message': 'LLM with the same name already exists', 'data': None}, 400

        # Create and add the new LLM configuration
        new_llm = LLMConfig(uri=uri, api_key=api_key, model=model, selected=selected)
        db.session.add(new_llm)
        db.session.commit()

        # Return success response with the new LLM configuration details
        return {'error': 0, 'message': 'LLM model added', 'data': new_llm.to_dict()}, 201

    # Static method to delete an existing LLM configuration from the database
    @staticmethod
    def delete_llm(id):
        llm_model = LLMConfig.query.get(id)  # Retrieve the LLM configuration by ID
        if not llm_model:
            # Return error if the model is not found
            return {'error': 1, 'message': 'LLM model not found', 'data': None}, 404

        # Delete the model and commit the changes to the database
        db.session.delete(llm_model)
        db.session.commit()

        # Return success response
        return {'error': 0, 'message': 'LLM model deleted', 'data': None}, 200

    # Static method to select an LLM configuration by ID
    @staticmethod
    def select_llm(id):
        all_llms = LLMConfig.query.all()  # Retrieve all LLM configurations
        for llm in all_llms:
            llm.selected = (llm.id == id)  # Mark the selected LLM
        db.session.commit()
        return {'error': 0, 'message': 'LLM configuration selected', 'data': id}, 200

    # Static method to get the currently selected LLM configuration
    @staticmethod
    def get_selected_llm():
        selected_llm = LLMConfig.query.filter_by(selected=True).first()  # Find the selected LLM
        config = {
            'uri': selected_llm.uri,
            'model': selected_llm.model,
            'api_key': selected_llm._decrypt_api_key()  # Decrypt the API key for use
        }
        return config
