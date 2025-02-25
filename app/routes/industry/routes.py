import logging
from flask import request, session
from . import industry
from .models import Industry
from ..auth.models import User

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

@industry.route('/industries', methods=['GET'])
def get_all_industry():
    """
    Retrieves all industries from the database.

    This endpoint returns a list of all industries stored in the database.

    Returns:
        dict: A JSON response containing the error code, message, and the list of industries.
    """
    industry = Industry.query.all()
    data = [industry.to_dict() for industry in industry]
    return {'error': 0, 'message': 'industry retrieved', 'industries': data}, 200


@industry.route('/industries/<industry_id>', methods=['GET'])
def get_industry(industry_id):
    """
    Retrieves a single industry from the database based on the provided industry ID.

    Args:
        industry_id (str): The ID of the industry to retrieve.

    Returns:
        dict: A JSON response containing the error code, message, and the industry data.
    """
    industry = Industry.get_industry(id=industry_id)
    if industry is None:
        return {'error': 1, 'message': 'Industry not found', 'data': None}, 404
    return {'error': 0, 'message': 'Industry retrieved', 'data': industry.to_dict()}, 200


@industry.route('/industries', methods=['POST'])
def add_industry():
    """
    Adds a new industry to the database.

    This endpoint allows authorized users (admins) to add a new industry. The user must be authenticated and have admin privileges.

    Returns:
        dict: A JSON response containing the error code, message, and any additional data.
    """
    user_id = session.get('user_id', None)
    if user_id is None:
        return {'error': 1, 'message': 'Unindustryorized', 'data': None}, 401

    user = User.get_user(id=user_id)
    if user is None or not user.admin:
        return {'error': 2, 'message': 'Permission denied', 'data': None}, 403

    name = request.json.get('name', None)
    description = request.json.get('description', None)
    
    if not name:
        return {'error': 3, 'message': 'Industry name is required', 'data': None}, 400

    err = Industry.add_industry(name=name, description=description)
    if err == 1:
        return {'error': 4, 'message': 'Industry already exists', 'data': None}, 400

    return {'error': 0, 'message': 'Industry added', 'data': None}, 201


@industry.route('/industries/<industry_id>', methods=['PUT'])
def update_industry(industry_id):
    """
    Updates the information of an existing industry.

    This endpoint allows admins to update an industry by modifying its name and/or description.

    Args:
        industry_id (str): The ID of the industry to update.

    Returns:
        dict: A JSON response containing the error code, message, and any updated data.
    """
    user_id = session.get('user_id', None)
    if user_id is None:
        return {'error': 1, 'message': 'Unindustryorized', 'data': None}, 401

    user = User.get_user(id=user_id)
    if user is None or not user.admin:
        return {'error': 2, 'message': 'Permission denied', 'data': None}, 403

    industry = Industry.get_industry(id=industry_id)
    if industry is None:
        return {'error': 3, 'message': 'Industry not found', 'data': None}, 404

    name = request.json.get('name', None)
    description = request.json.get('description', None)
    if not name and not description:
        return {'error': 4, 'message': 'No data to update', 'data': None}, 400

    industry.update_info(name=name, description=description)
    return {'error': 0, 'message': 'Industry updated', 'data': None}, 200


@industry.route('/industries/<industry_id>', methods=['DELETE'])
def delete_industry(industry_id):
    """
    Deletes an industry from the database.

    This endpoint allows admins to delete an industry from the database by its ID.

    Args:
        industry_id (str): The ID of the industry to delete.

    Returns:
        dict: A JSON response containing the error code, message, and any additional data.
    """
    user_id = session.get('user_id', None)
    if user_id is None:
        return {'error': 1, 'message': 'Unindustryorized', 'data': None}, 401

    user = User.get_user(id=user_id)
    if user is None or not user.admin:
        return {'error': 2, 'message': 'Permission denied', 'data': None}, 403

    err = Industry.delete_industry(id=industry_id)
    if err == 1:
        return {'error': 3, 'message': 'Industry not found', 'data': None}, 404

    return {'error': 0, 'message': 'Industry deleted', 'data': None}, 200
