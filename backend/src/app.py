from flask import Flask, render_template, request, make_response, redirect, url_for, jsonify
from flask_socketio import SocketIO, join_room, emit
from flask_cors import CORS
from src.database.database import Database
from src.current_documents.current_documents import CurrentDocuments
from src.codenames.codenames import Codenames
from src.hobby_tracker.hobby_tracker import HobbyTracker
from src.recipes_page.recipes_page import RecipesPage
from src.restaurants_page.restaurants_page import RestaurantsPage
from src.pantry_page.pantry_page import PantryPage
from src.notes_page.notes_page import NotesPage
from src.inventory_page.inventory_page import InventoryPage
from src.dominion.dominion import Dominion
import os
import sys
import socket

import traceback

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
database = None
current_documents = None
codenames = None
hobby_tracker = None
recipes_page = None
restaurants_page = None
pantry_page = None
notes_page = None
inventory_page = None
dominion = None


# Initialize app ----------------------------------------------------------------------------------------------
def initialize_app():
    global database
    global current_documents
    global codenames
    global hobby_tracker
    global recipes_page
    global restaurants_page
    global pantry_page
    global notes_page
    global inventory_page
    global dominion
    database = Database(is_production())
    current_documents = CurrentDocuments(database)
    codenames = Codenames(database)
    hobby_tracker = HobbyTracker(database)
    recipes_page = RecipesPage(database)
    restaurants_page = RestaurantsPage(database)
    pantry_page = PantryPage(database)
    notes_page = NotesPage(database)
    inventory_page = InventoryPage(database)
    dominion = Dominion(database)
    if is_production() and socket.gethostname() != "raspberrypi":
      should_run_app = query_yes_no("Running with production database. Continue?")
      if not should_run_app:
        os._exit(0)

def is_production():
  return app.config["ENV"] == "production"

# Current documents methods -------------------------------------------------------------------------------------

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
    document = request.json
    return jsonify(current_documents.edit_document(document))


@app.route("/add_document", methods=["POST"])
def add_document():
    document = request.json
    return jsonify(current_documents.add_document(document))


@app.route("/reorder_documents", methods=["POST"])
def reorder_documents():
    username = request.json["username"]
    document_ids = request.json["document_ids"]
    current_documents.reorder_documents(username, document_ids)
    return ""


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

# This is sent to all players in the current game to tell Vue to refresh the client.
def _dominion_send_socketio_refresh(game_data, player_triggering_update):
    players = game_data["playerOrder"]
    socketio.emit("refresh_dominion",
                  {"players": players,
                   "player_triggering_update": player_triggering_update,
                   "gameData": game_data}, broadcast=True)

# Hobby Tracker methods ----------------------------------------------------------------------------------------------

@app.route("/add_hobby", methods=["POST"])
def add_hobby():
    hobby = request.json
    return jsonify(hobby_tracker.add_hobby(hobby))

@app.route("/get_hobbies", methods=["POST"])
def get_hobbies():
    username = request.json["username"]
    return jsonify(hobby_tracker.get_hobbies(username))

@app.route("/delete_hobby", methods=["POST"])
def delete_hobby():
    hobby_id = request.json["id"]
    return jsonify(hobby_tracker.delete_hobby(hobby_id))

@app.route("/edit_hobbies", methods=["POST"])
def edit_hobbies():
    hobbies = request.json["hobbies"]
    hobby_tracker.edit_hobbies(hobbies)
    return ""


# Recipe / Restaurant methods ----------------------------------------------------------------------------------------

# NOTE: Adding an element artificially adds a children array to the javascript. This is to mirror the getRecipeData
# function and the getRestaurantData function.
@app.route("/add/<entity_type>", methods=["POST"])
def add_recipe_restaurant_entity(entity_type: str):
    data = request.json
    ret = None
    if entity_type == "cookbook":
        ret = recipes_page.add_cookbook(data["name"], data["notes"])
    elif entity_type == "recipe":
        ret = recipes_page.add_recipe(
            data["parent_id"], data["name"], data["category"], data["notes"])
    elif entity_type == "recipe_meal":
        ret = recipes_page.add_recipe_meal(
            data["parent_id"], data["date"], data["user_1_rating"], data["user_2_rating"], data["user_1_comments"],
            data["user_2_comments"])
    elif entity_type == "city":
        ret = restaurants_page.add_city(data["name"], data["state"], data["country"], data["notes"])
    elif entity_type == "restaurant":
        ret = restaurants_page.add_restaurant(
            data["parent_id"], data["name"], data["category"], data["address"], data["notes"])
    elif entity_type == "dish":
        ret = restaurants_page.add_dish(data["parent_id"], data["name"], data["category"], data["notes"])
    elif entity_type == "dish_meal":
        ret = restaurants_page.add_dish_meal(
            data["parent_id"], data["date"], data["user_1_rating"], data["user_2_rating"], data["user_1_comments"],
            data["user_2_comments"])
    if ret is not None:
        ret['children'] = []
    return jsonify(ret)

@app.route("/edit/<entity_type>", methods=["POST"])
def edit_recipe_restaurant_entity(entity_type: str):
    data = request.json
    ret = None
    if entity_type == "cookbook":
        ret = recipes_page.edit_cookbook(data["id"], data["name"], data["notes"])
    elif entity_type == "recipe":
        ret = recipes_page.edit_recipe(data["id"], data["name"], data["category"], data["notes"])
    elif entity_type == "recipe_meal":
        ret = recipes_page.edit_recipe_meal(
            data["id"], data["date"], data["user_1_rating"], data["user_2_rating"], data["user_1_comments"],
            data["user_2_comments"])
    elif entity_type == "city":
        ret = restaurants_page.edit_city(data["id"], data["name"], data["state"], data["country"], data["notes"])
    elif entity_type == "restaurant":
        ret = restaurants_page.edit_restaurant(
            data["id"], data["name"], data["category"], data["address"], data["notes"])
    elif entity_type == "dish":
        ret = restaurants_page.edit_dish(data["id"], data["name"], data["category"], data["notes"])
    elif entity_type == "dish_meal":
        ret = restaurants_page.edit_dish_meal(
            data["id"], data["date"], data["user_1_rating"], data["user_2_rating"], data["user_1_comments"],
            data["user_2_comments"])
    return jsonify(ret)

@app.route("/delete/<entity_type>", methods=["POST"])
def delete_recipe_restaurant_entity(entity_type: str):
    dataId = request.json["id"]
    ret = None
    if entity_type == "cookbook":
        ret = recipes_page.delete_cookbook(dataId)
    elif entity_type == "recipe":
        ret = recipes_page.delete_recipe(dataId)
    elif entity_type == "recipe_meal":
        ret = recipes_page.delete_recipe_meal(dataId)
    elif entity_type == "city":
        ret = restaurants_page.delete_city(dataId)
    elif entity_type == "restaurant":
        ret = restaurants_page.delete_restaurant(dataId)
    elif entity_type == "dish":
        ret = restaurants_page.delete_dish(dataId)
    elif entity_type == "dish_meal":
        ret = restaurants_page.delete_dish_meal(dataId)
    return jsonify(ret)

@app.route("/get_recipes_page_data", methods=["POST"])
def get_recipes_page_data():
    return jsonify(recipes_page.get_recipes_page_data())

@app.route("/get_restaurants_page_data", methods=["POST"])
def get_restaurants_page_data():
    return jsonify(restaurants_page.get_restaurants_page_data())


# Pantry ------------------------------------------------------------------------------------------------------

@app.route("/get_pantry_page", methods=["POST"])
def get_pantry_page():
    return jsonify(pantry_page.get_pantry_page_data())


@app.route("/edit_grocery_list", methods=["POST"])
def edit_grocery_list():
    grocery_list_id = request.json["id"]
    grocery_list = request.json["list"]
    return jsonify(pantry_page.edit_grocery_list(grocery_list_id, grocery_list))


@app.route("/edit_grocery_list_metadata", methods=["POST"])
def edit_grocery_list_metadata():
    grocery_list_id = request.json["id"]
    title = request.json["title"]
    store = request.json["store"]
    date = request.json["date"]
    return jsonify(pantry_page.edit_grocery_list_metadata(grocery_list_id, title, store, date))


@app.route("/delete_grocery_list", methods=["POST"])
def delete_grocery_list():
    grocery_list_id = request.json["id"]
    return jsonify(pantry_page.delete_grocery_list(grocery_list_id))


@app.route("/add_grocery_list", methods=["POST"])
def add_grocery_list():
    title = request.json["title"]
    store = request.json["store"]
    date = request.json["date"]
    return jsonify(pantry_page.add_grocery_list(title, store, date))


@app.route("/delete_pantry_item", methods=["POST"])
def delete_pantry_item():
    pantry_item = request.json["item"]
    return jsonify(pantry_page.delete_pantry_item(pantry_item))


@app.route("/add_pantry_item", methods=["POST"])
def add_pantry_item():
    pantry_item = request.json["item"]
    return jsonify(pantry_page.add_pantry_item(pantry_item))


@app.route("/delete_store_category", methods=["POST"])
def delete_store_category():
    store = request.json["store"]
    category = request.json["category"]
    return jsonify(pantry_page.delete_store_category(store, category))


@app.route("/add_store_category", methods=["POST"])
def add_store_category():
    store = request.json["store"]
    category = request.json["category"]
    label = request.json["label"]
    return jsonify(pantry_page.add_store_category(store, category, label))


@app.route("/delete_known_word", methods=["POST"])
def delete_known_word():
    known_word = request.json["word"]
    return jsonify(pantry_page.delete_known_word(known_word))


@app.route("/add_known_word", methods=["POST"])
def add_known_word():
    known_word = request.json["word"]
    category = request.json["category"]
    should_save = request.json["should_save"]
    return jsonify(pantry_page.add_known_word(known_word, category, should_save))


@app.route("/add_known_words", methods=["POST"])
def add_known_words():
    known_words = request.json
    return jsonify(pantry_page.add_known_words(known_words))


@app.route("/attempt_add_to_pantry", methods=["POST"])
def attempt_add_to_pantry():
    grocery_list_id = request.json["id"]
    return jsonify(pantry_page.add_to_pantry(grocery_list_id, False))


@app.route("/add_to_pantry", methods=["POST"])
def add_to_pantry():
    grocery_list_id = request.json["id"]
    return jsonify(pantry_page.add_to_pantry(grocery_list_id, True))

@app.route("/pantry_export_text", methods=["POST"])
def pantry_export_text():
    grocery_list_id = request.json["id"]
    return jsonify(pantry_page.get_export_text(grocery_list_id))

# Notes ------------------------------------------------------------------------------------------------------

@app.route("/get_notes_page", methods=["POST"])
def get_notes_page():
    return jsonify(notes_page.get_notes_page_data())


@app.route("/edit_note", methods=["POST"])
def edit_note():
    note_id = request.json["id"]
    note = request.json["text"]
    return jsonify(notes_page.edit_note(note_id, note))


@app.route("/edit_note_metadata", methods=["POST"])
def edit_note_metadata():
    note_id = request.json["id"]
    title = request.json["title"]
    return jsonify(notes_page.edit_note_metadata(note_id, title))


@app.route("/delete_note", methods=["POST"])
def delete_note():
    note_id = request.json["id"]
    return jsonify(notes_page.delete_note(note_id))


@app.route("/add_note", methods=["POST"])
def add_note():
    title = request.json["title"]
    return jsonify(notes_page.add_note(title))

@app.route("/reorder_notes", methods=["POST"])
def reorder_notes():
    note_ids = request.json["note_ids"]
    notes_page.reorder_notes(note_ids)
    return ""

# Inventory ------------------------------------------------------------------------------------------------------

@app.route("/get_inventory_page", methods=["POST"])
def get_inventory_page():
    return jsonify(inventory_page.get_inventory_page_data())


@app.route("/edit_box", methods=["POST"])
def edit_box():
    box_id = request.json["id"]
    box_text = request.json["text"]
    return jsonify(inventory_page.edit_box(box_id, box_text))


@app.route("/edit_box_metadata", methods=["POST"])
def edit_box_metadata():
    box_id = request.json["id"]
    title = request.json["title"]
    return jsonify(inventory_page.edit_box_metadata(box_id, title))


@app.route("/delete_box", methods=["POST"])
def delete_box():
    box_id = request.json["id"]
    return jsonify(inventory_page.delete_box(box_id))


@app.route("/add_box", methods=["POST"])
def add_box():
    title = request.json["title"]
    return jsonify(inventory_page.add_box(title))

# Dominion ----------------------------------------------------------------------------------------------------

@app.route("/generate_dominion_kingdom", methods=["POST"])
def generate_dominion_kingdom():
    return jsonify(dominion.generate_random_kingdom())

@app.route("/create_dominion_game", methods=["POST"])
def create_dominion_game():
    player1 = request.json["player1"]
    player2 = request.json["player2"]
    username = request.json["username"]
    game_data = dominion.create_game(player1, player2)
    _dominion_send_socketio_refresh(game_data, username)
    return jsonify(game_data)

@app.route("/dominion_get_latest_game", methods=["POST"])
def dominion_get_latest_game():
    username = request.json["username"]
    return jsonify(dominion.get_latest_game(username))

@app.route("/save_dominion_game", methods=["POST"])
def dominion_save_game():
    username = request.json["username"]
    game_id = request.json["gameId"]
    game_data = request.json["gameData"]
    dominion.update_game(game_id, game_data)
    _dominion_send_socketio_refresh(game_data, username)
    return ""

# Error handling ----------------------------------------------------------------------------------------------

@app.errorhandler(Exception)
def handle_error(e):
    tb = traceback.format_exc()
    response = jsonify({'exception': tb})
    response.status_code = 500
    return response


# From http://code.activestate.com/recipes/577058/
def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

initialize_app()


if __name__ == "__main__":
    socketio.run(app, debug=True)
