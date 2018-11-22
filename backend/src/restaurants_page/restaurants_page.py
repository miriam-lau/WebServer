from typing import Dict
import psycopg2


class RestaurantsPage:
    def __init__(self, database):
        self._database = database

    def add_city(self, name, state, country, notes):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "INSERT INTO cities(name, state, country, notes) VALUES(%s, %s, %s, %s) RETURNING *",
                (name, state, country, notes))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_restaurant(self, parent_id, name, category, address, notes):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "INSERT INTO restaurants(parent_id, name, category, address, notes) VALUES(%s, %s, %s, %s, %s) " +
                "RETURNING *",
                (parent_id, name, category, address, notes))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_dish(self, parent_id, name, category, notes):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "INSERT INTO dishes(parent_id, name, category, notes) VALUES(%s, %s, %s, %s) RETURNING *",
                (parent_id, name, category, notes))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_dish_meal(self, parent_id, date, user_1_rating, user_2_rating, user_1_comments, user_2_comments):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "INSERT INTO dish_meals(parent_id, date, user_1_rating, user_2_rating, user_1_comments, " +
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

    def edit_city(self, id, name, state, country, notes):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "UPDATE cities SET name = %s, state = %s, country = %s, notes = %s where id = %s RETURNING *",
                (name, state, country, notes, id))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def edit_restaurant(self, id, name, category, address, notes):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "UPDATE restaurants SET name = %s, category = %s, address = %s, notes = %s where id = %s RETURNING *",
                (name, category, address, notes, id))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def edit_dish(self, id, name, category, notes):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "UPDATE dishes SET name = %s, category = %s, notes = %s where id = %s RETURNING *",
                (name, category, notes, id))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def edit_dish_meal(self, id, date, user_1_rating, user_2_rating, user_1_comments, user_2_comments):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "UPDATE dish_meals set date = %s, user_1_rating = %s, user_2_rating = %s, user_1_comments = %s, " +
                "user_2_comments = %s where id = %s RETURNING *",
                (date, user_1_rating, user_2_rating, user_1_comments, user_2_comments, id))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def delete_city(self, id):
        cur = self._database.get_cursor()

        try:
            cur.execute("DELETE from cities where id = %s RETURNING id", (id,))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def delete_restaurant(self, id):
        cur = self._database.get_cursor()

        try:
            cur.execute("DELETE from restaurants where id = %s RETURNING id", (id,))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def delete_dish(self, id):
        cur = self._database.get_cursor()

        try:
            cur.execute("DELETE from dishes where id = %s RETURNING id", (id,))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def delete_dish_meal(self, id):
        cur = self._database.get_cursor()

        try:
            cur.execute("DELETE from dish_meals where id = %s RETURNING id", (id,))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    # Returns an object with the following properties:
    #   cities: A map of cities ids to cities objects. This is a single root node which has a hardcoded
    #       id of 0.
    #   city: A map of city ids to city objects.
    #   restaurant: A map of restaurant ids to restaurant objects.
    #   dish: A map of dish ids to dish objects.
    #   dish_meal: A map of dish meal ids to dish meal objects.
    def get_restaurants_page_data(self):
        cur = self._database.get_cursor()

        try:
            ret = {}

            cities_dict = {}
            cities_dict[0] = {
                "entity_type": "cities",
                "children": []
            }

            city_dict = {}
            cur.execute("SELECT * from cities")
            for city in cur.fetchall():
                city["children"] = []
                city_dict[city["id"]] = city
                cities_dict[city["parent_id"]]["children"].append(city["id"])

            restaurant_dict = {}
            cur.execute("SELECT * from restaurants")
            for restaurant in cur.fetchall():
                restaurant["children"] = []
                restaurant_dict[restaurant["id"]] = restaurant
                city_dict[restaurant["parent_id"]]["children"].append(restaurant["id"])

            dish_dict = {}
            cur.execute("SELECT * from dishes")
            for dish in cur.fetchall():
                dish["children"] = []
                dish_dict[dish["id"]] = dish
                restaurant_dict[dish["parent_id"]]["children"].append(dish["id"])

            dish_meal_dict = {}
            cur.execute("SELECT * from dish_meals")
            for dish_meal in cur.fetchall():
                dish_meal_dict[dish_meal["id"]] = dish_meal
                dish_dict[dish_meal["parent_id"]]["children"].append(dish_meal["id"])

            ret["cities"] = cities_dict
            ret["city"] = city_dict
            ret["restaurant"] = restaurant_dict
            ret["dish"] = dish_dict
            ret["dish_meal"] = dish_meal_dict

            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise
