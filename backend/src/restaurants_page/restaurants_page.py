from typing import Dict
import psycopg2


class RestaurantsPage:
    def __init__(self, database):
        self._database = database

    def add_city(self, name, state, country, notes):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "INSERT INTO cities(name, state, country, notes) VALUES(%s, %s, %s, %s)", 
                (name, state, country, notes))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_restaurant(self, city_id, name, category, address, notes):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "INSERT INTO restaurants(city_id, name, category, address, notes) VALUES(%s, %s, %s, %s, %s)", 
                (city_id, name, category, address, notes))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_dish(self, restaurant_id, name, category, notes):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "INSERT INTO dishes(restaurant_id, name, category, notes) VALUES(%s, %s, %s, %s)", 
                (restaurant_id, name, category, notes))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_dish_meal(self, dish_id, date, user_1_rating, user_2_rating, user_1_comments, user_2_comments):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "INSERT INTO dish_meals(dish_id, date, user_1_rating, user_2_rating, user_1_comments, " + 
                "user_2_comments) VALUES(%s, %s, %s, %s, %s, %s)", 
                (dish_id, date, user_1_rating, user_2_rating, user_1_comments, user_2_comments))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise
