from typing import Dict
import psycopg2


class RecipesPage:
    def __init__(self, database):
        self._database = database

    def add_cookbook(self, name, notes):
        if not name:
            raise Exception('Name must not be empty.')

        cur = self._database.get_cursor()

        try:
            cur.execute("INSERT INTO cookbooks(name, notes) VALUES(%s, %s) RETURNING *", (name, notes))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_recipe(self, parent_id, name, priority, category, notes):
        if not name:
            raise Exception('Name must not be empty.')

        cur = self._database.get_cursor()

        try:
            cur.execute(
                "INSERT INTO recipes(parent_id, name, priority, category, notes) VALUES(%s, %s, %s, %s, %s) " +
                "RETURNING *",
                (parent_id, name, priority, category, notes))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_recipe_meal(self, parent_id, date, user_1_rating, user_2_rating, user_1_comments, user_2_comments):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "INSERT INTO recipe_meals(parent_id, date, user_1_rating, user_2_rating, user_1_comments, " +
                "user_2_comments) VALUES(%s, %s, %s, %s, %s, %s) RETURNING *",
                (parent_id, date, user_1_rating, user_2_rating, user_1_comments, user_2_comments))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def edit_cookbook(self, id, name, notes):
        if not name:
            raise Exception('Name must not be empty.')

        cur = self._database.get_cursor()

        try:
            cur.execute("UPDATE cookbooks SET name = %s, notes = %s where id = %s RETURNING *", (name, notes, id))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def edit_recipe(self, id, name, priority, category, notes):
        if not name:
            raise Exception('Name must not be empty.')

        cur = self._database.get_cursor()

        try:
            cur.execute(
                "UPDATE recipes set name = %s, priority = %s, category = %s, notes = %s where id = %s RETURNING *",
                (name, priority, category, notes, id))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def edit_recipe_meal(self, id, date, user_1_rating, user_2_rating, user_1_comments, user_2_comments):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "UPDATE recipe_meals set date = %s, user_1_rating = %s, user_2_rating = %s, user_1_comments = %s " +
                ", user_2_comments = %s where id = %s RETURNING *",
                (date, user_1_rating, user_2_rating, user_1_comments, user_2_comments, id))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def delete_cookbook(self, id):
        cur = self._database.get_cursor()

        try:
            cur.execute("DELETE from cookbooks where id = %s RETURNING *", (id,))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def delete_recipe(self, id):
        cur = self._database.get_cursor()

        try:
            cur.execute("DELETE from recipes where id = %s RETURNING *", (id,))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def delete_recipe_meal(self, id):
        cur = self._database.get_cursor()

        try:
            cur.execute("DELETE from recipe_meals where id = %s RETURNING *", (id,))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    # Returns an object with the following properties:
    #   cookbooks: A map of cookbooks ids to cookbooks objects. This is a single root node which has a hardcoded
    #       id of 0.
    #   cookbook: A map of cookbook ids to cookbook objects.
    #   recipe: A map of recipe ids to recipe objects.
    #   recipe_meal: A map of recipe meal ids to recipe meal objects.
    def get_recipes_page_data(self):
        cur = self._database.get_cursor()

        try:
            ret = {}

            cookbooks_dict = {}
            cookbooks_dict[0] = {
                "entity_type": "cookbooks",
                "children": []
            }

            cookbook_dict = {}
            cur.execute("SELECT * from cookbooks")
            for cookbook in cur.fetchall():
                cookbook["children"] = []
                cookbook_dict[cookbook["id"]] = cookbook
                cookbooks_dict[cookbook["parent_id"]]["children"].append(cookbook["id"])

            recipe_dict = {}
            cur.execute("SELECT * from recipes")
            for recipe in cur.fetchall():
                recipe["children"] = []
                recipe_dict[recipe["id"]] = recipe
                cookbook_dict[recipe["parent_id"]]["children"].append(recipe["id"])

            recipe_meal_dict = {}
            cur.execute("SELECT * from recipe_meals")
            for recipe_meal in cur.fetchall():
                recipe_meal_dict[recipe_meal["id"]] = recipe_meal
                recipe_dict[recipe_meal["parent_id"]]["children"].append(recipe_meal["id"])

            ret["cookbooks"] = cookbooks_dict
            ret["cookbook"] = cookbook_dict
            ret["recipe"] = recipe_dict
            ret["recipe_meal"] = recipe_meal_dict

            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise
