import datetime
import logging
import os
from uuid import uuid4
from cryptography.fernet import Fernet
from dotenv import load_dotenv

from .. import db

root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
os.chdir(root)
dotenv_path = "app/routes/llm_config/.env"
load_dotenv(dotenv_path)

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    print("SECRET_KEY not found in .env. Generating a new one...")
    SECRET_KEY = Fernet.generate_key().decode("utf-8")
    with open(dotenv_path, "a") as dotenv_file:
        dotenv_file.write(f"SECRET_KEY={SECRET_KEY}\n")
    print("New SECRET_KEY saved to .env")

cipher_suite = Fernet(SECRET_KEY)

def get_uuid():
    """
    Generates a unique identifier using UUID4.

    Returns:
        str: The generated UUID in hexadecimal format.
    """
    return uuid4().hex


class LLMConfig(db.Model):
    """
    The LLMConfig class represents a configuration for a Large Language Model (LLM).
    This class includes fields such as the model's URI, encrypted API key, creation time, and update time.
    """
    __tablename__ = 'llm'

    id = db.Column(db.String(32), primary_key=True,
                   unique=True, default=get_uuid) 
    model = db.Column(db.String(255), nullable=False, unique=True) 
    uri = db.Column(db.String(255), nullable=False, unique=False)
    api_key_encrypted = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    selected = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        """
        Converts the LLMConfig object to a dictionary format for easy JSON serialization.

        Returns:
            dict: A dictionary representation of the LLMConfig object with model, URI, API key (partial), etc.
        """
        return {
            'id': self.id,
            'uri': self.uri,
            'model': self.model,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'api_key': self.get_partial_api_key(), 
            'selected': self.selected
        }

    def __init__(self, uri, api_key, model, selected):
        """
        Initialize a new LLMConfig instance.

        Args:
            uri (str): The URI for the LLM.
            api_key (str): The API key for the LLM (will be encrypted).
            model (str): The name of the LLM model.
            selected (bool): Indicates whether this LLM is selected or not.
        """
        self.uri = uri
        self.api_key_encrypted = self._encrypt_api_key(api_key)
        self.model = model
        self.selected = selected

    def _encrypt_api_key(self, api_key):
        """
        Encrypts the given API key using the cipher suite.

        Args:
            api_key (str): The API key to encrypt.

        Returns:
            str: The encrypted API key.
        """
        return cipher_suite.encrypt(api_key.encode('utf-8')).decode('utf-8')

    def _decrypt_api_key(self):
        """
        Decrypts the encrypted API key.

        Returns:
            str: The decrypted API key.
        """
        return cipher_suite.decrypt(self.api_key_encrypted.encode('utf-8')).decode('utf-8')

    def get_partial_api_key(self):
        """
        Retrieves a partial API key for security purposes (first 8 characters).

        Returns:
            str: A partial API key.
        """
        api_key = self._decrypt_api_key()
        return api_key[:8]

    def check_api_key(self, api_key):
        """
        Compares the provided API key with the decrypted one to verify authenticity.

        Args:
            api_key (str): The API key to check.

        Returns:
            bool: True if the provided key matches the decrypted key, False otherwise.
        """
        return api_key == self._decrypt_api_key()

    def update_uri(self, new_uri):
        """
        Updates the URI of the LLMConfig and commits the changes to the database.

        Args:
            new_uri (str): The new URI to set.
        """
        self.uri = new_uri
        self.updated_at = datetime.datetime.now()
        db.session.commit()

    def update_api_key(self, new_api_key):
        """
        Updates the encrypted API key of the LLMConfig and commits the changes to the database.

        Args:
            new_api_key (str): The new API key to encrypt and store.
        """
        self.api_key_encrypted = self._encrypt_api_key(new_api_key)
        self.updated_at = datetime.datetime.now()
        db.session.commit()

    @staticmethod
    def add_llm(uri, api_key, model, selected):
        """
        Adds a new LLM configuration to the database.

        Args:
            uri (str): The URI of the LLM.
            api_key (str): The API key of the LLM.
            model (str): The model name of the LLM.
            selected (bool): Whether this LLM is selected.

        Returns:
            dict: A response message indicating success or failure, and the LLM data (if successful).
        """
        existing_llm = LLMConfig.query.filter_by(model=model).first()
        if existing_llm:
            return {'error': 1, 'message': 'LLM with the same name already exists', 'data': None}, 400

        new_llm = LLMConfig(uri=uri, api_key=api_key, model=model, selected=selected)
        db.session.add(new_llm)
        db.session.commit()

        return {'error': 0, 'message': 'LLM model added', 'data': new_llm.to_dict()}, 201

    @staticmethod
    def delete_llm(id):
        """
        Deletes an LLM configuration by its ID.

        Args:
            id (str): The ID of the LLM to delete.

        Returns:
            dict: A response message indicating success or failure.
        """
        llm_model = LLMConfig.query.get(id)
        if not llm_model:
            return {'error': 1, 'message': 'LLM model not found', 'data': None}, 404

        db.session.delete(llm_model)
        db.session.commit()

        return {'error': 0, 'message': 'LLM model deleted', 'data': None}, 200

    @staticmethod
    def select_llm(id):
        """
        Selects an LLM configuration by setting it as the active model (selected).

        Args:
            id (str): The ID of the LLM to select.

        Returns:
            dict: A response message indicating success.
        """
        all_llms = LLMConfig.query.all()
        for llm in all_llms:
            llm.selected = (llm.id == id)
        db.session.commit()
        return {'error': 0, 'message': 'LLM configuration selected', 'data': id}, 200

    @staticmethod
    def get_selected_llm():
        """
        Retrieves the currently selected LLM configuration.

        Returns:
            dict: The configuration of the selected LLM, including URI, model, and decrypted API key.
        """
        selected_llm = LLMConfig.query.filter_by(selected=True).first()
        config = {
            'uri': selected_llm.uri,
            'model': selected_llm.model,
            'api_key': selected_llm._decrypt_api_key()
        }
        return config
