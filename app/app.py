import os
from flask import Flask, Response, json, jsonify, request, send_from_directory
import google.generativeai as genai
import mysql.connector
from werkzeug.security import generate_password_hash
import logging

from utils.jwt_utils import generate_jwt
from utils.jwt_utils import verify_jwt

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "incident_nav_auth"
}


def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Erreur de connexion à la base de données : {err}")
        return None

def hash_password(password):
    print(generate_password_hash(password))
    return generate_password_hash(password)

@app.route('/')
def login():
    directory = os.path.dirname(__file__)
    filepath = os.path.join(directory, 'client/login.html')
    with open(filepath, 'r') as file:
        html = file.read()
    return html, 200, {'Content-Type': 'text/html'}


@app.route('/incidentnavigator')
def navigator():
    auth_header = request.headers.get('Authorization')

    logging.debug(f'auth = {auth_header}')
    
    if not auth_header:
        return jsonify({"error": "Token manquant"}), 401

    try:
        token = auth_header.split(" ")[1]
    except IndexError:
        return jsonify({"error": "Format d'Authorization invalide"}), 401

    logging.debug(token)
    verification_result = verify_jwt(token)

    if "error" in verification_result:
        return jsonify(verification_result), 401

    directory = os.path.dirname(__file__)
    filepath = os.path.join(directory, 'client/navigator.html')

    try:
        with open(filepath, 'r') as file:
            html = file.read()
        return html, 200, {'Content-Type': 'text/html'}
    except FileNotFoundError:
        return jsonify({"error": "Fichier introuvable"}), 500


@app.route('/style/<path:filename>')
def serve_style(filename):
    directory = os.path.join(os.path.dirname(__file__), 'client', 'style')
    return send_from_directory(directory, filename)


@app.route('/script/<path:filename>')
def serve_script(filename):
    directory = os.path.join(os.path.dirname(__file__), 'client', 'script')
    return send_from_directory(directory, filename)


@app.route('/login', methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Le nom d'utilisateur et le mot de passe sont requis."}), 400

    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({"error": "Erreur de connexion à la base de données."}), 500

        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE user = %s AND pwd = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            token = generate_jwt(username)
            return jsonify({"message": "Connexion réussie", "username": username, "token": token}), 200
        else:
            return jsonify({"error": "Nom d'utilisateur ou mot de passe incorrect."}), 401

    except Exception as e:
        print(f"Erreur : {e} ; {e.with_traceback(None)}")
        return jsonify({"error": "Une erreur est survenue lors de la connexion."}), 500


@app.route('/rest/v1/chat/completions', methods=["POST"])
def runLLM():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token manquant"}), 401

    try:
        token = auth_header.split(" ")[1]
    except IndexError:
        return jsonify({"error": "Format d'Authorization invalide"}), 401

    verification_result = verify_jwt(token)
    if "error" in verification_result:
        return jsonify(verification_result), 401

    request_body = request.get_json()
    msg = request_body['text']
    context = request_body['context']
    prompt = request_body['prompt']

    print(msg)
    print(context)
    print(prompt)

    final_msg = []

    for ctx in context:
        print()
        print(f'ctx : {ctx} \n')
        final_msg.append({'role': 'user', 'parts': ctx['user']})
        final_msg.append({'role': 'assistant', 'parts': ctx['assistant']})

    final_msg.append({'role': 'user', 'parts': msg})

    print(get_api_key('api_key.txt'))
    genai.configure(api_key=get_api_key('api_key.txt'))
    model = genai.GenerativeModel(
        "gemini-1.5-flash", system_instruction=[prompt])
    response = model.generate_content(final_msg, stream=True)

    return Response(convert_response(response), content_type='text/event-stream')


def convert_response(response):
    for chunk in response:
        msg = {"choices": [
            {"delta": {"content": f"{chunk.text}"}, "finish_reason": None}]}

        yield f"data: {json.dumps(msg)}\n\n"

    final_chunk = {
        "choices": [
            {"delta": {"content": ""}, "finish_reason": "stop"}
        ]
    }
    yield f"data: {json.dumps(final_chunk)}\n\n"


def get_api_key(file_name):
    try:
        directory = os.path.dirname(__file__)
        file_path = os.path.join(directory, file_name)
        with open(file_path, 'r') as file:
            api_key = file.read().strip()
        return api_key
    except FileNotFoundError:
        print(f"Error: The file {file_path} does not exist.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
