from flask import Blueprint

# Création du Blueprint
llm = Blueprint('llm', __name__)

from . import routes
