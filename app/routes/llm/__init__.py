from flask import Blueprint

# Création du Blueprint auth
llm = Blueprint('llm', __name__)

from . import routes