from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify
from flask_socketio import SocketIO, join_room, emit
from flask_cors import CORS
from .database.database import Database
from .current_documents.current_documents import CurrentDocuments


# Must correspond to what is used in Vue.
USERNAME_REQUEST_NAME = "username"
ID_REQUEST_NAME = "id"
DOCUMENT_REQUEST_NAME = "document"


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
database = None
current_documents = None


# Initialize app ----------------------------------------------------------------------------------------------
def initialize_app():
    global database
    global current_documents
    database = Database()
    current_documents = CurrentDocuments(database)


# Current documents methods -------------------------------------------------------------------------------------

# TODO: This is totally insecure.
@app.route("/get_current_documents", methods=["POST"])
def get_current_documents():
    username = request.json[USERNAME_REQUEST_NAME]
    return jsonify(current_documents.get_current_documents(username))


@app.route("/delete_document", methods=["POST"])
def delete_document():
    document_id = request.json[ID_REQUEST_NAME]
    return jsonify(current_documents.delete_document(document_id))


@app.route("/edit_document", methods=["POST"])
def edit_document():
    document_id = request.json[ID_REQUEST_NAME]
    document = request.json[DOCUMENT_REQUEST_NAME]
    return jsonify(current_documents.edit_document(document_id, document))


@app.route("/add_document", methods=["POST"])
def add_document():
    document = request.json[DOCUMENT_REQUEST_NAME]
    return jsonify(current_documents.add_document(document))


initialize_app()


if __name__ == "__main__":
    socketio.run(app, debug=True)
