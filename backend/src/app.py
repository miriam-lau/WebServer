from flask import Flask, request, jsonify
from flask_cors import CORS
from src.database.database import Database
from src.recipes_page.recipes_page import RecipesPage
from src.restaurants_page.restaurants_page import RestaurantsPage
from src.pantry_page.pantry_page import PantryPage
from src.inventory_page.inventory_page import InventoryPage
import os
import sys
import socket

import traceback

app = Flask(__name__)
CORS(app)
database = None
recipes_page = None
restaurants_page = None
pantry_page = None
inventory_page = None

# Initialize app ----------------------------------------------------------------------------------------------


def initialize_app():
    global database
    global recipes_page
    global restaurants_page
    global pantry_page
    global inventory_page
    database = Database(is_production())
    recipes_page = RecipesPage(database)
    restaurants_page = RestaurantsPage(database)
    pantry_page = PantryPage(database)
    inventory_page = InventoryPage(database)
    if is_production() and socket.gethostname() != "raspberrypi":
        should_run_app = query_yes_no(
            "Running with production database. Continue?")
        if not should_run_app:
            os._exit(0)


def is_production():
    return app.config["ENV"] == "production"


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
        ret = restaurants_page.add_city(
            data["name"], data["state"], data["country"], data["notes"])
    elif entity_type == "restaurant":
        ret = restaurants_page.add_restaurant(
            data["parent_id"], data["name"], data["category"], data["address"], data["notes"])
    elif entity_type == "dish":
        ret = restaurants_page.add_dish(
            data["parent_id"], data["name"], data["category"], data["notes"])
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
        ret = recipes_page.edit_recipe(
            data["id"], data["name"], data["category"], data["notes"])
    elif entity_type == "recipe_meal":
        ret = recipes_page.edit_recipe_meal(
            data["id"], data["date"], data["user_1_rating"], data["user_2_rating"], data["user_1_comments"],
            data["user_2_comments"])
    elif entity_type == "city":
        ret = restaurants_page.edit_city(
            data["id"], data["name"], data["state"], data["country"], data["notes"])
    elif entity_type == "restaurant":
        ret = restaurants_page.edit_restaurant(
            data["id"], data["name"], data["category"], data["address"], data["notes"])
    elif entity_type == "dish":
        ret = restaurants_page.edit_dish(
            data["id"], data["name"], data["category"], data["notes"])
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
    store = request.json["store"]
    date = request.json["date"]
    return jsonify(pantry_page.edit_grocery_list_metadata(grocery_list_id, store, date))


@app.route("/delete_grocery_list", methods=["POST"])
def delete_grocery_list():
    grocery_list_id = request.json["id"]
    return jsonify(pantry_page.delete_grocery_list(grocery_list_id))


@app.route("/add_grocery_list", methods=["POST"])
def add_grocery_list():
    store = request.json["store"]
    date = request.json["date"]
    return jsonify(pantry_page.add_grocery_list(store, date))


@app.route("/delete_pantry_item", methods=["POST"])
def delete_pantry_item():
    pantry_item = request.json["item"]
    return jsonify(pantry_page.delete_pantry_item(pantry_item))


@app.route("/add_pantry_item", methods=["POST"])
def add_pantry_item():
    pantry_item = request.json["item"]
    return jsonify(pantry_page.add_pantry_item(pantry_item))


@app.route("/add_store_aisles", methods=["POST"])
def add_store_aisles():
    store = request.json["store"]
    categories_to_aisles = request.json["categories_to_aisles"]
    pantry_page.add_store_aisles(store, categories_to_aisles)
    return ''


@app.route("/add_store", methods=["POST"])
def add_store():
    store = request.json["store"]
    return jsonify(pantry_page.add_store(store))


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


@app.route("/validate_known_words", methods=["POST"])
def validate_known_words():
    grocery_list_id = request.json["id"]
    return jsonify(pantry_page.validate_known_words(grocery_list_id))


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


# Error handling ----------------------------------------------------------------------------------------------


@app.errorhandler(Exception)
def handle_error(e):
    tb = traceback.format_exc()
    response = jsonify({'exception': tb})
    response.status_code = 500
    return response


# From http://code.activestate.com/recipes/577058/
def query_yes_no(question, default="no"):
    print(default)
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


if __name__ == "__main__":
    pass


initialize_app()
