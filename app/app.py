import os
import sqlite3
import time
from flask import Flask, Response, json, jsonify, request, g, send_from_directory
import google.generativeai as genai

app = Flask(__name__)


@app.route('/')
def test_endpoint():
    return jsonify({"message": "OK"}), 200


@app.route('/incidentnavigator')
def home():
    # Load html from file
    directory = os.path.dirname(__file__)
    filepath = os.path.join(directory, 'client/navigator.html')
    with open(filepath, 'r') as file:
        html = file.read()
    return html, 200, {'Content-Type': 'text/html'}

# CSS


@app.route('/style.css')
def style():
    directory = os.path.dirname(__file__)
    filepath = os.path.join(directory, 'client/style.css')
    with open(filepath, 'r') as file:
        css = file.read()
    return css, 200, {'Content-Type': 'text/css'}


@app.route('/script.js')
def serve_script():
    directory = os.path.dirname(__file__)
    filepath = os.path.join(directory, 'client/script.js')
    with open(filepath, 'r') as file:
        js = file.read()
    return js, 200, {'Content-Type': 'application/javascript'}


@app.route('/rest/v1/chat/completions', methods=["POST"])
def runLLM():
    print(get_api_key('api_key.txt'))
    genai.configure(api_key=get_api_key('api_key.txt'))
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content("Explain how AI works", stream=True)

    def generate_response():
        response_chunks = [
            {"choices": [
                {"delta": {"content": "Hello, "}, "finish_reason": None}]},
            {"choices": [
                {"delta": {"content": "this is a "}, "finish_reason": None}]},
            {"choices": [
                {"delta": {"content": "streaming response."}, "finish_reason": None}]},
            {"choices": [
                {"delta": {"content": "streaming response."}, "finish_reason": "stop"}]}
        ]
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

    return Response(generate_response(), content_type='text/event-stream')


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
