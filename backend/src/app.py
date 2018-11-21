from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify
from flask_socketio import SocketIO, join_room, emit
from flask_cors import CORS
from src.database.database import Database
from src.current_documents.current_documents import CurrentDocuments
from src.codenames.codenames import Codenames
from src.hobby_tracker.hobby_tracker import HobbyTracker
from src.recipes_page.recipes_page import RecipesPage
from src.restaurants_page.restaurants_page import RestaurantsPage


app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
database = None
current_documents = None
codenames = None
hobby_tracker = None
recipes_page = None
restaurants_page = None


# Initialize app ----------------------------------------------------------------------------------------------
def initialize_app():
    global database
    global current_documents
    global codenames
    global hobby_tracker
    global recipes_page
    global restaurants_page
    database = Database()
    current_documents = CurrentDocuments(database)
    codenames = Codenames(database)
    hobby_tracker = HobbyTracker(database)
    recipes_page = RecipesPage(database)
    restaurants_page = RestaurantsPage(database)

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


@app.route("/reorder_documents", methods=["POST"])
def reorder_documents():
    username = request.json["username"]
    document_ids = request.json["document_ids"]
    return jsonify(current_documents.reorder_documents(username, document_ids))


# Codenames methods ----------------------------------------------------------------------------------------------

# TODO: Make the socketio less hacky. It shouldn't update for everyone whenever a game state is changed.
@app.route("/codenames_create_game", methods=["POST"])
def codenames_create_game():
    username = request.json["username"]
    player1 = request.json["player1"]
    player2 = request.json["player2"]
    game_id = codenames.create_game(player1, player2)
    _codenames_send_socketio_refresh(game_id, username)
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
    _codenames_send_socketio_refresh(game_id, player)
    return ""


@app.route("/codenames_end_guesses", methods=["POST"])
def codenames_end_guesses():
    game_id = request.json["game_id"]
    player = request.json["username"]
    codenames.end_guesses(game_id, player)
    _codenames_send_socketio_refresh(game_id, player)
    return ""


@app.route("/codenames_guess", methods=["POST"])
def codenames_guess():
    game_id = request.json["game_id"]
    player = request.json["username"]
    word = request.json["word"]
    codenames.guess(game_id, player, word)
    _codenames_send_socketio_refresh(game_id, player)
    return ""


# This is sent to all players in the current game to tell Vue to refresh the client.
def _codenames_send_socketio_refresh(game_id, player_triggering_update):
    players = codenames.get_players_in_game(game_id)
    socketio.emit("refresh_codenames",
                  {"players": players, "player_triggering_update": player_triggering_update},
                  broadcast=True)

# Hobby Tracker methods ----------------------------------------------------------------------------------------------

@app.route("/add_hobby", methods=["POST"])
def add_hobby():
    hobby = request.json["hobby"]
    hobby_tracker.add_hobby(hobby)
    return ""

@app.route("/get_hobbies", methods=["POST"])
def get_hobbies():
    username = request.json["username"]
    return jsonify(hobby_tracker.get_hobbies(username))

@app.route("/delete_hobby", methods=["POST"])
def delete_hobby():
    hobby_id = request.json["id"]
    return jsonify(hobby_tracker.delete_hobby(hobby_id))

# Recipe / Restaurant methods ----------------------------------------------------------------------------------------

@app.route("/add/<entity_type>", methods=["POST"])
def add_recipe_restaurant_entity(entity_type: str):
    data = request.json
    if entity_type == "cookbook":
        recipes_page.add_cookbook(data["name"], data["notes"])
    elif entity_type == "recipe":
        recipes_page.add_recipe(data["cookbook_id"], data["name"], data["priority"], data["category"], data["notes"])
    elif entity_type == "recipe_meal":
        recipes_page.add_recipe_meal(
            data["recipe_id"], data["date"], data["user_1_rating"], data["user_2_rating"], data["user_1_comments"],
            data["user_2_comments"])
    elif entity_type == "city":
        restaurants_page.add_city(data["name"], data["state"], data["country"], data["notes"])
    elif entity_type == "restaurant":
        restaurants_page.add_restaurant(data["city_id"], data["name"], data["category"], data["address"], data["notes"])
    elif entity_type == "dish":
        restaurants_page.add_dish(data["restaurant_id"], data["name"], data["category"], data["notes"])
    elif entity_type == "dish_meal":
        restaurants_page.add_dish_meal(
            data["dish_id"], data["date"], data["user_1_rating"], data["user_2_rating"], data["user_1_comments"],
            data["user_2_comments"])
    return ""

# ----------------------------------------------------------------------------------------------


initialize_app()


if __name__ == "__main__":
    socketio.run(app, debug=True)
