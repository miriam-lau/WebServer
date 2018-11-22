from typing import Dict
import psycopg2


# TODO: Consider splitting this file up into the current one and a hobby_tracker_database.py file.
class HobbyTracker:
    def __init__(self, database):
        self._database = database

    def add_hobby(self, hobby):
        cur = self._database.get_cursor()

        try:
            cur.execute(
                "SELECT * from hobby_tracker where username = %s ORDER BY sort_order desc", (hobby["username"],))
            last_hobby = cur.fetchone()
            new_sort_order = last_hobby['sort_order'] + 1 if last_hobby is not None else 0
            cur.execute("INSERT INTO hobby_tracker(username, hobby, sort_order, assigned_hours_per_week) " +
                        "VALUES(%s, %s, %s, %s)",
                        (hobby["username"], hobby["hobby"], new_sort_order, hobby["assigned_hours_per_week"]))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def get_hobbies(self, username):
        cur = self._database.get_cursor()

        try:
            cur.execute("SELECT * from hobby_tracker where username = %s", (username,))
            hobbies = cur.fetchall()
            cur.close()
            return hobbies
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def delete_hobby(self, hobby_id):
        cur = self._database.get_cursor()

        try:
            cur.execute("DELETE from hobby_tracker where id = %s", (hobby_id,))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise

    def edit_hobbies(self, hobbies):
        cur = self._database.get_cursor()
#hobby object does not have "completed_hours_for_week" as a property anymore.
        try:
            for hobby in hobbies:
                cur.execute("UPDATE hobby_tracker SET hobby = %s, assigned_hours_per_week = %s where id = %s",
                            (hobby["hobby"], hobby["assigned_hours_per_week"], hobby["id"]))
                cur.execute("INSERT INTO hobby_completed_hours_timestamped(hobby_id, completed_hours_for_week) " +
                            "VALUES(%s, %s)", (hobby["id"], hobby["completed_hours_for_week"]))
                self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise
