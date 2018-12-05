from typing import Dict, List
import psycopg2


class InventoryPage:
    def __init__(self, database):
        self._database = database

    # Returns an array containing the data for the inventory page.
    def get_inventory_page_data(self) -> Dict:
        cur = self._database.get_cursor()

        try:
            cur.execute("SELECT * from inventory order by id")
            inventory = cur.fetchall()
            cur.close()
            return inventory
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def delete_box(self, box_id):
        cur = self._database.get_cursor()

        try:
            cur.execute("DELETE from inventory where id = %s RETURNING *", (box_id,))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def edit_box_metadata(self, box_id, box_title):
        if not box_title:
            raise Exception('Title must not be empty.')

        cur = self._database.get_cursor()

        try:
            cur.execute("UPDATE inventory SET title = %s where id = %s RETURNING *",
                        (box_title, box_id))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def edit_box(self, box_id, text):
        cur = self._database.get_cursor()

        try:
            cur.execute("UPDATE inventory SET text = %s where id = %s RETURNING *",
                        (text, box_id))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def add_box(self, title):
        if not title:
            raise Exception('Title must not be empty.')

        cur = self._database.get_cursor()

        try:
            cur.execute("INSERT INTO inventory(title, text) VALUES(%s, '') RETURNING *", (title,))
            ret = cur.fetchone()
            self._database.commit()
            cur.close()
            return ret
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise
