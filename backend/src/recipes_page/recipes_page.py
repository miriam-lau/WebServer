from typing import Dict
import psycopg2


class RecipesPage:
    def __init__(self, database):
        self._database = database

    def add_cookbook(self, name, notes):
        cur = self._database.get_cursor()

        try:
            cur.execute("INSERT INTO cookbooks(name, notes) VALUES(%s, %s)", (name, notes))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_recipe(self, cookbook_id, name, priority, category, notes):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "INSERT INTO recipes(cookbook_id, name, priority, category, notes) VALUES(%s, %s, %s, %s, %s)",
                (cookbook_id, name, priority, category, notes))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_recipe_meal(self, recipe_id, date, user_1_rating, user_2_rating, user_1_comments, user_2_comments):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "INSERT INTO recipe_meals(recipe_id, date, user_1_rating, user_2_rating, user_1_comments, " +
                "user_2_comments) VALUES(%s, %s, %s, %s, %s, %s)",
                (recipe_id, date, user_1_rating, user_2_rating, user_1_comments, user_2_comments))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def get_recipes_page_data(self):
        cur = self._database.get_cursor()

        try:
            ret = {}

            cookbooks_list = []
            cookbook_dict = {}
            cur.execute("SELECT * from cookbooks")
            for cookbook in cur.fetchall():
                cookbook["recipes"] = []
                cookbook_dict[cookbook["id"]] = cookbook
                cookbooks_list.append(cookbook["id"])

            recipe_dict = {}
            cur.execute("SELECT * from recipes")
            for recipe in cur.fetchall():
                recipe["recipe_meals"] = []
                recipe_dict[recipe["id"]] = recipe
                cookbook_dict[recipe["cookbook_id"]]["recipes"].append(recipe["id"])

            recipe_meal_dict = {}
            cur.execute("SELECT * from recipe_meals")
            for recipe_meal in cur.fetchall():
                recipe_meal_dict[recipe_meal["id"]] = recipe_meal
                recipe_dict[recipe_meal["recipe_id"]]["recipe_meals"].append(recipe_meal["id"])

            ret["cookbooks_list"] = cookbooks_list
            ret["cookbooks"] = cookbook_dict
            ret["recipes"] = recipe_dict
            ret["recipe_meals"] = recipe_meal_dict

            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise
