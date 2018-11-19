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
            cur.execute("INSERT INTO hobby_tracker(username, hobby, sort_order, assigned_hours_per_week, " +
                        "completed_hours_this_week, completed) VALUES(%s, %s, %s, %s, %s, %s)",
                        (hobby["username"], hobby["hobby"], new_sort_order, hobby["assigned_hours_per_week"], 0, False))
            self._database.commit()
            cur.close()
        except psycopg2.Error:
            self._database.rollback()
            cur.close()
            raise
