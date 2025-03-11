from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from .chatbot import handle_query
from vector_search import get_chat_history, show_history
from mongo_connection import get_mongo_collections
import os
 
app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['POST'])
def query():
    return handle_query(request)

@app.route('/get_chat_history/<session_id>', methods=['GET'])
def chat_history(session_id):
    if not session_id or session_id == "undefined":
        return jsonify({'error': 'session_id no proporcionado'}), 400
    return get_chat_history(session_id)

@app.route('/historial', methods=['GET'])
def historial():
    return show_history()

#if __name__ == '__main__':
 #   port = int(os.environ.get("WEBSITES_PORT", 5001))  # Usa 8000 en Azure, 5001 localmente
  #  app.run(host="0.0.0.0", port=port, debug=True)
