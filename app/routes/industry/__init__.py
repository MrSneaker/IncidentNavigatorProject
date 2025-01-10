from flask import Blueprint
from flask_session import Session
from flask_cors import CORS
from flask_bcrypt import Bcrypt

industry = Blueprint('industry', __name__)
session = Session()
cors = CORS()
bcrypt = Bcrypt()

from .models import Industry, db

# Import des routes d'authentification
from . import routes
