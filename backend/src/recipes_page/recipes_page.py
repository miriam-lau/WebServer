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
