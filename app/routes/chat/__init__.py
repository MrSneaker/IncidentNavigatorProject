from flask import Blueprint


# Création du Blueprint auth
chat = Blueprint('chat', __name__)

from .models import Message, Chat, db

# Import des routes d'authentification
from . import routes

