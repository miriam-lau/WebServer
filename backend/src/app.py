from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify
from flask_socketio import SocketIO, join_room, emit
from flask_cors import CORS
from src.database.database import Database
from src.current_documents.current_documents import CurrentDocuments
from src.codenames.codenames import Codenames


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
database = None
current_documents = None
codenames = None


# Initialize app ----------------------------------------------------------------------------------------------
def initialize_app():
    global database
    global current_documents
    global codenames
    database = Database()
    current_documents = CurrentDocuments(database)
    codenames = Codenames(database)

# Current documents methods -------------------------------------------------------------------------------------


# TODO: This is totally insecure.
@app.route("/get_current_documents", methods=["POST"])
def get_current_documents():
    username = request.json["username"]
    return jsonify(current_documents.get_current_documents(username))


@app.route("/delete_document", methods=["POST"])
def delete_document():
    document_id = request.json["id"]
    return jsonify(current_documents.delete_document(document_id))


@app.route("/edit_document", methods=["POST"])
def edit_document():
    document_id = request.json["id"]
    document = request.json["document"]
    return jsonify(current_documents.edit_document(document_id, document))


@app.route("/add_document", methods=["POST"])
def add_document():
    document = request.json["document"]
    return jsonify(current_documents.add_document(document))


# Codenames methods ----------------------------------------------------------------------------------------------

@app.route("/codenames_create_game", methods=["POST"])
def codenames_create_game():
    username = request.json["username"]
    player1 = request.json["player1"]
    player2 = request.json["player2"]
    codenames.create_game(player1, player2)
    return ""


@app.route("/codenames_get_latest_game", methods=["POST"])
def codenames_get_latest_game():
    username = request.json["username"]
    return jsonify(codenames.get_latest_game(username))


@app.route("/codenames_give_hint", methods=["POST"])
def codenames_give_hint():
    game_id = request.json["game_id"]
    player = request.json["username"]
    hint_word = request.json["hint_word"]
    hint_number = request.json["hint_number"]
    codenames.give_hint(game_id, player, hint_word, hint_number)
    return ""


@app.route("/codenames_end_guesses", methods=["POST"])
def codenames_end_guesses():
    game_id = request.json["game_id"]
    player = request.json["username"]
    codenames.end_guesses(game_id, player)
    return ""


@app.route("/codenames_guess", methods=["POST"])
def codenames_guess():
    game_id = request.json["game_id"]
    player = request.json["username"]
    word = request.json["word"]
    codenames.guess(game_id, player, word)
    return ""


initialize_app()


if __name__ == "__main__":
    socketio.run(app, debug=True)
