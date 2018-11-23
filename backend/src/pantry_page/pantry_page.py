from typing import Dict, List
import psycopg2


class PantryPage:
    def __init__(self, database):
        self._database = database

    # Returns an object containing the data for the pantry page. Consists of the keys:
    #   grocery_lists: An array of grocery list objects.
    #   pantry: An array of pantry items.
    def get_pantry_page_data(self) -> Dict:
        cur = self._database.get_cursor()

        try:
            cur.execute("SELECT * from grocery_lists order by id")
            grocery_lists = cur.fetchall()
            cur.execute("SELECT * from pantry")
            pantry_items = cur.fetchall()
            return {
                'grocery_lists': grocery_lists,
                'pantry': pantry_items
            }
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def delete_grocery_list(self, grocery_list_id):
        cur = self._database.get_cursor()

        try:
            cur.execute("DELETE from grocery_lists where id = %s", (grocery_list_id,))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def edit_grocery_list_metadata(self, grocery_list_id, grocery_list_title):
        if not grocery_list_title:
            raise Exception('Title must not be empty.')

        cur = self._database.get_cursor()

        try:
            cur.execute("UPDATE grocery_lists SET title = %s where id = %s",
                        (grocery_list_title, grocery_list_id))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def edit_grocery_list(self, grocery_list_id, grocery_list):
        cur = self._database.get_cursor()

        try:
            cur.execute("UPDATE grocery_lists SET list = %s where id = %s",
                        (grocery_list, grocery_list_id))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_grocery_list(self, title):
        if not title:
            raise Exception('Title must not be empty.')

        cur = self._database.get_cursor()

        try:
            cur.execute("INSERT INTO grocery_lists(title) VALUES(%s)", (title,))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise
