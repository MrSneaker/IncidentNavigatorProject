import datetime
import os
from uuid import uuid4
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from .. import db

dotenv_path = "app/routes/llm/.env"
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
    return uuid4().hex


class LLM(db.Model):
    __tablename__ = 'llm'
    id = db.Column(db.String(32), primary_key=True,
                   unique=True, default=get_uuid)
    model = db.Column(db.String(255), nullable=False, unique=True)
    uri = db.Column(db.String(255), nullable=False, unique=True)
    api_key_encrypted = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(
        db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'uri': self.uri,
            'model': self.model,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'api_key': self.get_partial_api_key()
        }

    def __init__(self, uri, api_key, model):
        self.uri = uri
        self.api_key_encrypted = self._encrypt_api_key(api_key)
        self.model = model

    def _encrypt_api_key(self, api_key):
        return cipher_suite.encrypt(api_key.encode('utf-8')).decode('utf-8')

    def _decrypt_api_key(self):
        return cipher_suite.decrypt(self.api_key_encrypted.encode('utf-8')).decode('utf-8')

    def get_partial_api_key(self):
        api_key = self._decrypt_api_key()
        return api_key[:8]

    def check_api_key(self, api_key):
        return api_key == self._decrypt_api_key()

    def update_uri(self, new_uri):
        self.uri = new_uri
        self.updated_at = datetime.datetime.now()
        db.session.commit()

    def update_api_key(self, new_api_key):
        self.api_key_encrypted = self._encrypt_api_key(new_api_key)
        self.updated_at = datetime.datetime.now()
        db.session.commit()

    @staticmethod
    def add_llm(uri, api_key, model):
        existing_llm = LLM.query.filter_by(uri=uri).first()
        if existing_llm:
            return {'error': 1, 'message': 'LLM with the same URI already exists', 'data': None}, 400

        new_llm = LLM(uri=uri, api_key=api_key, model=model)
        db.session.add(new_llm)
        db.session.commit()

        return {'error': 0, 'message': 'LLM model added', 'data': new_llm.to_dict()}, 201

    @staticmethod
    def delete_llm(id):
        llm_model = LLM.query.get(id)
        if not llm_model:
            return {'error': 1, 'message': 'LLM model not found', 'data': None}, 404

        db.session.delete(llm_model)
        db.session.commit()

        return {'error': 0, 'message': 'LLM model deleted', 'data': None}, 200
